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

from fhir_kindling.fhir_query import FHIRQuery
from fhir_kindling.fhir_server.auth import generate_auth
from fhir_kindling.fhir_query.query_functions import query_with_string
from fhir_kindling.fhir_server.response import ResourceCreateResponse
from fhir_kindling.serde import flatten_bundle
from oauthlib.oauth2 import BackendApplicationClient
from dotenv import load_dotenv, find_dotenv
import pendulum

import re


class FhirServer:

    def __init__(self, api_address: str, username: str = None, password: str = None, token: str = None,
                 client_id: str = None, client_secret: str = None, oidc_provider_url: str = None,
                 fhir_server_type: str = "hapi"):

        # server definition values
        self.fhir_server_type = fhir_server_type
        self.api_address = self._validate_api_address(api_address)
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

    def query(self, resource: Union[Resource, fhir.resources.FHIRAbstractModel] = None) -> FHIRQuery:
        """
        Initialize a FHIR query against the server with the given resource

        Args:
            resource: the FHIR resource to query from the server

        Returns: a FHIRQuery object that can be further modified with filters and conditions before being executed
        against the server
        """
        return FHIRQuery(self.api_address, resource, auth=self.auth, session=self.session)

    def raw_query(self, query_string: str) -> FHIRQuery:
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

        query = FHIRQuery(self.api_address, resource, session=self.session)
        query.set_query_string(valid_query_string)
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
        response = self._upload_resource(resource)
        response.raise_for_status()

        return ResourceCreateResponse(server_response=response, resource=resource)

    def add_all(self, resources: List[Union[Resource, dict]]):
        bundle = self._make_bundle_from_resource_list(resources)
        response = self._upload_bundle(bundle)
        return response.json()

    def add_bundle(self, bundle: Union[Bundle, dict, str]):
        # todo check this
        if isinstance(bundle, dict):
            bundle = Bundle(**bundle)

        elif isinstance(bundle, str):
            bundle = Bundle(**json.loads(bundle))

        response = self._upload_bundle(bundle)
        return response.json()

    def _make_bundle_from_resource_list(self, resources: List[Union[FHIRAbstractModel, dict]]) -> Bundle:
        upload_bundle = Bundle.construct()
        upload_bundle.type = "transaction"
        upload_bundle.entry = []

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
    def _make_bundle_request_entry(resource: FHIRAbstractModel) -> BundleEntry:
        entry = BundleEntry().construct()
        entry.request = BundleEntry(
            **{
                "method": "POST",
                "url": resource.get_resource_type()
            }
        )
        entry.resource = resource

        return entry


    def _upload_bundle(self, bundle: Bundle) -> Response:
        r = self.session.post(self.api_address, json=bundle.dict())
        r.raise_for_status()

        return r

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
        url = self.api_address + "/metadata"
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
        return CapabilityStatement(**self._meta_data)

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
    def _validate_api_address(api_address: str) -> str:
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
