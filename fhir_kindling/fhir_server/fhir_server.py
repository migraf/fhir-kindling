import json
import os
from typing import List, Union, Tuple

import pandas as pd
import requests
from fhir.resources import FHIRAbstractModel
from requests import Response
import requests.auth
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.capabilitystatement import CapabilityStatement
from requests_oauthlib import OAuth2Session
import fhir.resources
from requests_toolbelt import user_agent

from fhir_kindling.fhir_query import FHIRQuery
from fhir_kindling.fhir_server.auth import generate_auth
from fhir_kindling.fhir_server.response import ResourceCreateResponse, BundleCreateResponse
from fhir_kindling.serde import flatten_bundle
from oauthlib.oauth2 import BackendApplicationClient
import pendulum

import re


class FhirServer:

    def __init__(self, api_address: str, username: str = None, password: str = None, token: str = None,
                 client_id: str = None, client_secret: str = None, oidc_provider_url: str = None,
                 fhir_server_type: str = "hapi"):

        # server definition values
        self.fhir_server_type = fhir_server_type
        self.api_address = self.validate_api_address(api_address)
        self._meta_data = None

        # possible basic auth class vars
        self.username = username
        self.password = password

        # token oidc auth class vars
        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
        self.oidc_provider_url = oidc_provider_url
        self.token_expiration = None

        # setup the session
        self.session = requests.Session()
        self._setup()

    @classmethod
    def from_env(cls, no_auth: bool = False):
        api_address = _api_address_from_env()
        server_type = os.getenv("FHIR_SERVER_TYPE")

        if no_auth:
            return FhirServer(api_address=api_address, fhir_server_type=server_type)
        else:
            env_auth = _auth_info_from_env()
            # static token
            if isinstance(env_auth, str):
                return cls(api_address=api_address, token=env_auth, fhir_server_type=server_type)
            # username and password
            elif isinstance(env_auth, tuple) and len(env_auth) == 2:
                return cls(api_address=api_address, username=env_auth[0], password=env_auth[1],
                           fhir_server_type=server_type)
            # oauth2/oidc
            elif isinstance(env_auth, tuple) and len(env_auth) == 3:
                return cls(api_address=api_address, client_id=env_auth[0], client_secret=env_auth[1],
                           oidc_provider_url=env_auth[2], fhir_server_type=server_type)
            else:
                raise EnvironmentError("Authentication information could not be loaded from environment")

    def query(self, resource: Union[Resource, fhir.resources.FHIRAbstractModel] = None,
              output_format: str = "json") -> FHIRQuery:
        """
        Initialize a FHIR query against the server with the given resource

        Args:
            output_format: the output format to request from the fhir server (json or xml) defaults to json
            resource: the FHIR resource to query from the server

        Returns: a FHIRQuery object that can be further modified with filters and conditions before being executed
        against the server
        """
        return FHIRQuery(self.api_address, resource, auth=self.auth, session=self.session, output_format=output_format)

    def raw_query(self, query_string: str, output_format: str = "json") -> FHIRQuery:
        """
        Execute a raw query string against the server

        Args:
            query_string:
            output_format:
            limit:
            count:

        Returns:

        """
        valid_query_string, resource = self._validate_query_string_and_parse_resource(query_string)
        query = FHIRQuery(self.api_address, resource, session=self.session, output_format=output_format)
        query.set_query_string(valid_query_string)
        print(query.query_url)
        return query

    def add(self, resource: Union[Resource, dict]) -> ResourceCreateResponse:
        """
        Upload a resource to the server

        Args:
            resource: dictionary containing the resource or FHIR resource object to be uploaded to the server

        Returns:

        """
        # parse the resource given as dictionary into a fhir resource model
        if isinstance(resource, dict):
            resource_type = resource.get("resourceType")
            if not resource_type:
                raise ValueError("No resource type defined in resource dictionary")
            resource = fhir.resources.construct_fhir_element(resource_type, resource)
        else:
            resource = resource.validate(resource)
        response = self._upload_resource(resource)
        response.raise_for_status()

        return ResourceCreateResponse(server_response_dict=response.headers, resource=resource)

    def add_all(self, resources: List[Union[Resource, dict]]):
        bundle = self._make_bundle_from_resource_list(resources)
        response = self._upload_bundle(bundle)
        return response

    def add_bundle(self, bundle: Union[Bundle, dict, str], validate_entries: bool = True) -> BundleCreateResponse:
        # todo check this
        # create bundle and validate it
        if isinstance(bundle, dict):
            bundle = Bundle(**bundle)
        elif isinstance(bundle, str):
            bundle = Bundle(**json.loads(bundle))
        else:
            bundle = Bundle.validate(bundle)
        # check that all entries are bundle requests with methods post/put
        if validate_entries:
            self._validate_upload_bundle_entries(bundle.entry)

        transaction_response = self._upload_bundle(bundle)
        return transaction_response

    def _make_bundle_from_resource_list(self, resources: List[Union[FHIRAbstractModel, dict]]) -> Bundle:
        upload_bundle = Bundle.construct()
        upload_bundle.type = "transaction"
        upload_bundle.entry = []

        # initialize fhir model instances from dict
        if isinstance(resources[0], dict):
            resources = [fhir.resources.construct_fhir_element(
                resource.get("resourceType"),
                resource
            )
                for resource in resources
            ]
        for resource in resources:
            entry = self._make_bundle_request_entry(resource)
            upload_bundle.entry.append(entry)

        return upload_bundle

    @staticmethod
    def _validate_upload_bundle_entries(entries: List[BundleEntry]):
        for i, entry in enumerate(entries):
            if entry.request.method.lower() not in ["post", "put"]:
                raise ValueError(f"Entry {i}:  method is not in [post, put]")

    @staticmethod
    def _make_bundle_request_entry(resource: FHIRAbstractModel) -> BundleEntry:
        entry = BundleEntry().construct()
        entry.request = BundleEntryRequest(
            **{
                "method": "POST",
                "url": resource.get_resource_type()
            }
        )
        entry.resource = resource

        return entry

    def _upload_bundle(self, bundle: Bundle) -> BundleCreateResponse:
        r = self.session.post(url=self.api_address, data=bundle.json(return_bytes=True))
        print(r.headers)
        r.raise_for_status()
        bundle_response = BundleCreateResponse(r, bundle)
        return bundle_response

    def _upload_resource(self, resource: Resource) -> Response:
        url = self.api_address + "/" + resource.get_resource_type()
        r = requests.post(url=url, headers=self._headers, auth=self.auth, json=resource.dict())
        return r

    @staticmethod
    def _format_output(bundle_response: dict, output_format: str) -> Union[dict, pd.DataFrame, Bundle]:
        if output_format in {"json", "raw"}:
            return bundle_response
        elif output_format == "parsed":
            return Bundle(**bundle_response)
        elif output_format == "df":
            return flatten_bundle(bundle_response)

    def _get_meta_data(self):
        url = self.api_address + "/metadata?_format=json"
        r = self.session.get(url)
        r.raise_for_status()
        response = r.json()
        self._meta_data = response

    def _setup(self):
        self.session.auth = self.auth
        self.session.headers.update(self._headers)

    @property
    def capabilities(self) -> CapabilityStatement:
        if not self._meta_data:
            self._get_meta_data()
        # todo change back to return capability statement resource
        return self._meta_data

    @property
    def auth(self) -> Union[requests.auth.AuthBase, None]:
        # todo more info about auth status and validation
        # OIDC authentication
        if self.client_id:
            self._get_oidc_token()
            return generate_auth(token=self.token)
        # basic or static token authentication
        elif self.username and self.password:
            return generate_auth(self.username, self.password)

        elif self.token:
            return generate_auth(token=self.token)
        else:
            print("No authentication given")
            return None

    def _get_oidc_token(self):

        # get a new token if it is expired or not yet set
        if (self.token_expiration and pendulum.now() > self.token_expiration) or not self.token:
            print("Requesting new token")
            client = BackendApplicationClient(client_id=self.client_id)
            oauth = OAuth2Session(client=client)
            token = oauth.fetch_token(
                token_url=self.oidc_provider_url,
                client_secret=self.client_secret,
                client_id=self.client_id
            )
            self.token = token["access_token"]
            self.token_expiration = pendulum.now() + pendulum.duration(seconds=token["expires_in"])

    @property
    def _headers(self):
        return {"Content-Type": "application/fhir+json"}

    @staticmethod
    def _validate_query_string_and_parse_resource(query_string_input: str) -> Tuple[str, FHIRAbstractModel]:
        if query_string_input[0] != "/":
            valid_query = "/" + query_string_input
        else:
            valid_query = query_string_input

        resource_string = valid_query.split("/")[1].split("?")[0]
        resource = fhir.resources.get_fhir_model_class(resource_string).construct()
        return valid_query, resource

    @staticmethod
    def validate_api_address(api_address: str) -> str:
        """
        Validate that api address is well formed and remove trailing / if present
        https://stackoverflow.com/a/7160778/3838313

        Args:
            api_address: base endpoint for the fhir rest api of the server

        Returns:
            the validated api address

        """

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'[A-Za-z0-9_-]*|'  # single word with hyphen/underscore for docker
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, api_address):
            if api_address[-1] == "/":
                api_address = api_address[:-1]
            return api_address

        else:
            raise ValueError(f"Malformed API URL: {api_address}")


def _api_address_from_env() -> str:
    # load FHIR_API_URL
    api_url = os.getenv("FHIR_API_URL")
    if not api_url:
        api_url = os.getenv("FHIR_SERVER_URL")
    if not api_url:
        raise EnvironmentError("No FHIR api address specified")
    return FhirServer.validate_api_address(api_url)


def _auth_info_from_env() -> Union[str, Tuple[str, str], Tuple[str, str, str]]:
    # First try to load basic auth information
    username = os.getenv("FHIR_USER")
    if username:
        password = os.getenv("FHIR_PW")
        if not password:
            raise EnvironmentError(f"No password specified for user: {username}")
        else:
            print(f"Basic auth environment info found -> ({username}:******)")
            return username, password
    # Static token auth
    token = os.getenv("FHIR_TOKEN")
    if username and token:
        raise EnvironmentError("Conflicting auth information, bother username and token present.")
    if token:
        print("Found static auth token")
        return token
    # oauth2/oidc authentication
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    oidc_provider_url = os.getenv("OIDC_PROVIDER_URL")

    if username and client_id:
        raise EnvironmentError("Conflicting auth information, bother username and client id present")
    if token and client_id:
        raise EnvironmentError("Conflicting auth information, bother static token and client id present")

    if client_id and not client_secret:
        raise EnvironmentError("Insufficient auth information, client id specified but no client secret found.")

    if (client_id and client_secret) and not oidc_provider_url:
        raise EnvironmentError("Insufficient auth information, client id and secret "
                               "specified but no provider URL found")
    if client_id and client_secret and oidc_provider_url:
        print(f"Found OIDC auth configuration for client <{client_id}> with provider {oidc_provider_url}")
        return client_id, client_secret, oidc_provider_url
