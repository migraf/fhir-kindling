import json
import os
from typing import List, Union, Tuple
import requests
from fhir.resources import FHIRAbstractModel
from requests import Response
import requests.auth
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.capabilitystatement import CapabilityStatement
from fhir.resources.reference import Reference
from fhir.resources.fhirresourcemodel import FHIRResourceModel
from requests_oauthlib import OAuth2Session
import fhir.resources
import re
from oauthlib.oauth2 import BackendApplicationClient
import pendulum

from fhir_kindling.fhir_query import FHIRQuery
from fhir_kindling.fhir_query.query_response import QueryResponse
from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters
from fhir_kindling.fhir_server.auth import generate_auth
from fhir_kindling.fhir_server.server_responses import ResourceCreateResponse, BundleCreateResponse, ServerSummary


class FhirServer:

    def __init__(self, api_address: str, username: str = None, password: str = None, token: str = None,
                 client_id: str = None, client_secret: str = None, oidc_provider_url: str = None,
                 auth: requests.auth.AuthBase = None, headers: dict = None,
                 fhir_server_type: str = "hapi"):
        """
        Initialize a FHIR server connection
        Args:
            api_address: the base endpoint of the fhir server api
            username: username for basic auth
            password: password for basic auth
            token: token for static token auth
            client_id: client id for oauth2
            client_secret: client secret for oauth2
            oidc_provider_url: provider url for oauth2
            auth: optional auth object to authenticate against a server
            headers: optional additional headers to be added to the session
            fhir_server_type: type of fhir server (hapi, blaze, etc.)
        """

        # server definition values
        self.fhir_server_type = fhir_server_type
        self.api_address = self.validate_api_address(api_address)
        self._meta_data = None
        self.auth = None

        # possible basic auth class vars
        self.username = username
        self.password = password

        # token oidc auth class vars
        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
        self.oidc_provider_url = oidc_provider_url
        self.token_expiration = None

        self._auth = auth
        self._headers = headers

        # setup the session
        self.session = requests.Session()
        self._setup()

    def query(self, resource: Union[Resource, FHIRAbstractModel, str] = None,
              query_parameters: FHIRQueryParameters = None,
              output_format: str = "json", count: int = 5000) -> FHIRQuery:
        """
        Initialize a FHIR query against the server with the given resource or query parameters

        Args:
            output_format: the output format to request from the fhir server (json or xml) defaults to json
            query_parameters: optionally pass in a query parameters object to use for the query
            resource: the FHIR resource to query from the server
            count: the number of resources requested per page

        Returns: a FHIRQuery object that can be further modified with filters and conditions before being executed
        against the server
        """
        if resource:
            return FHIRQuery(self.api_address, resource, auth=self.auth, session=self.session,
                             output_format=output_format, count=count)
        else:
            return FHIRQuery(self.api_address, auth=self.auth, session=self.session, query_parameters=query_parameters,
                             count=count, output_format=output_format)

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

        query_parameters = FHIRQueryParameters.from_query_string(query_string)
        query = FHIRQuery(
            self.api_address,
            resource=query_parameters.resource,
            query_parameters=query_parameters,
            session=self.session,
            output_format=output_format
        )
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

        return ResourceCreateResponse(server_response_dict=dict(response.headers), resource=resource)

    def add_all(self, resources: List[Union[Resource, dict]]) -> BundleCreateResponse:
        """
        Upload a list of resources to the server, after packaging them into a bundle
        Args:
            resources: list of resources to upload to the server, either dictionary or FHIR resource objects

        Returns: Bundle create response from the fhir server

        """
        bundle = self._make_bundle_from_resource_list(resources)
        response = self._upload_bundle(bundle)
        return response

    def add_bundle(self, bundle: Union[Bundle, dict, str], validate_entries: bool = True) -> BundleCreateResponse:
        # create bundle and validate it
        if isinstance(bundle, dict):
            bundle = Bundle(**bundle)
        elif isinstance(bundle, str):
            bundle = Bundle.parse_raw(bundle)
        else:
            bundle = Bundle.validate(bundle)
        # check that all entries are bundle requests with methods post/put
        if validate_entries:
            self._validate_upload_bundle_entries(bundle.entry)

        transaction_response = self._upload_bundle(bundle)
        return transaction_response

    def update(self, resources: List[Union[FHIRResourceModel, dict]]):
        """
        Update a list of resources that exist on the server
        Args:
            resources: List of updated resources coming to send to the server

        Returns: Bundle update response from the fhir server

        """

        # todo check that the resources exist and have an id?
        # batch update transaction
        update_bundle = Bundle.construct()
        update_bundle.type = "transaction"
        update_bundle.entry = []
        for resource in resources:
            if isinstance(resource, dict):
                resource_type = resource.get("resourceType")
                if not resource_type:
                    raise ValueError("No resource type defined in resource dictionary")
                resource = fhir.resources.construct_fhir_element(resource_type, resource)
            elif isinstance(resource, FHIRResourceModel):
                resource = resource.validate(resource)
            else:
                raise ValueError(f"Invalid resource type {type(resource)}")
            # make the transaction entry
            entry = self._make_transaction_entry(resource.relative_path(), "PUT")
            # add the resource to the entry
            entry.resource = resource
            # validate the entry and append it to the bundle
            update_bundle.entry.append(BundleEntry(**entry.dict()))

        # validate bundle
        update_bundle = Bundle(**update_bundle.dict())
        response = self.session.post(self.api_address, data=update_bundle.json())
        response.raise_for_status()

        return response.json()

    def delete(self,
               resources: List[Union[FHIRResourceModel, dict]] = None,
               references: List[Union[str, Reference]] = None,
               query: FHIRQuery = None):
        """
        Delete resources from the server. Either resources or references must be specified.
        Args:
            resources: Resources coming from the server containing an id to delete
            references: references {Resource}/{id} to delete
            query: query to use to find resources to delete

        Returns: Bundle delete response from the fhir server

        """
        if resources and references:
            raise ValueError("Cannot delete based on resources and references at the same time")
        if resources and query:
            raise ValueError("Cannot delete based on resources and query at the same time")
        if references and query:
            raise ValueError("Cannot delete based on references and query at the same time")

        transaction_bundle = self._make_delete_transaction(resources, references, query)

        response = self.session.post(self.api_address, json=transaction_bundle.dict())
        response.raise_for_status()

        return response

    def transfer(self, target_server: 'FhirServer', query: FHIRQuery = None,
                 bundle: Union[Bundle, dict, str, bytes] = None):
        if query and bundle:
            raise ValueError("Cannot transfer based on query and bundle at the same time")
        if query:
            # todo execute query, get bundle, parse references, upload bundle
            raise NotImplementedError("Transfer by query is not implemented yet")

        elif bundle:
            if isinstance(bundle, dict):
                bundle = Bundle(**bundle)
            elif isinstance(bundle, str):
                bundle = Bundle.parse_raw(bundle)

        response = self._transfer_bundle(bundle, target_server)

    def _transfer_bundle(self, bundle: Bundle, target_server: 'FhirServer') -> Bundle:
        # todo
        staged_upload = self._resolve_references(bundle)

    def _resolve_references(self, bundle: Bundle):
        # todo
        pass

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

    def _make_delete_transaction(self, resources: List[Union[Resource, dict]] = None,
                                 references: List[Union[str, Reference]] = None, query: QueryResponse = None) -> Bundle:
        delete_bundle = Bundle.construct()
        delete_bundle.type = "transaction"
        delete_bundle.entry = []

        if resources:
            print(resources)
            if isinstance(resources[0], dict):
                resources = [fhir.resources.construct_fhir_element(
                    resource.get("resourceType"),
                    resource
                )
                    for resource in resources
                ]

            delete_references = [res.relative_path() for res in resources]
        elif references:
            if isinstance(references[0], Reference):
                references = [ref.reference for ref in references]
            delete_references = references
        elif query:

            delete_references = [resource.relative_path() for resource in query.resources]
        else:
            raise ValueError("No resources or references provided")

        bundle_entries = [self._make_transaction_entry(ref, method="DELETE") for ref in delete_references]
        delete_bundle.entry = bundle_entries
        return delete_bundle

    @staticmethod
    def _make_transaction_entry(reference: str, method: str = "POST") -> BundleEntry:
        entry = BundleEntry.construct()
        entry.request = BundleEntryRequest(
            **{
                "method": method,
                "url": reference
            }
        )

        return entry

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
        r.raise_for_status()
        bundle_response = BundleCreateResponse(r, bundle)
        return bundle_response

    def _upload_resource(self, resource: Resource) -> Response:
        url = self.api_address + "/" + resource.get_resource_type()
        r = requests.post(url=url, headers=self.headers, auth=self.auth, json=resource.dict())
        return r

    def _get_meta_data(self):
        url = self.api_address + "/metadata"
        r = self.session.get(url)
        r.raise_for_status()
        response = r.json()
        self._meta_data = response

    def _setup(self):
        self.auth = self._validate_auth()
        self.session.auth = self.auth
        self.session.headers.update(self.headers)

    @property
    def capabilities(self) -> CapabilityStatement:
        if not self._meta_data:
            self._get_meta_data()
        return CapabilityStatement(**self._meta_data)

    @property
    def rest_resources(self) -> List[str]:
        return [capa.type for capa in self.capabilities.rest[0].resource]

    def summary(self) -> ServerSummary:
        summary = self._make_server_summary()
        return summary

    def _make_server_summary(self) -> ServerSummary:
        resources = []
        summary = {
            "name": self.api_address
        }
        for resource in self.rest_resources:
            url = self.api_address + "/" + resource + "?_summary=count"
            r = self.session.get(url)
            r.raise_for_status()

            resource_dict = {
                "resource": resource,
                "count": r.json().get("total")
            }
            resources.append(resource_dict)

        summary["resources"] = resources
        summary = ServerSummary(**summary)
        return summary

    @property
    def headers(self):
        headers = {"Content-Type": "application/fhir+json"}
        if self._headers:
            headers.update(self._headers)
        return headers

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

    def _validate_auth(self) -> Union[requests.auth.AuthBase, None]:
        if self._auth and (self.username or self.password):
            raise ValueError(
                "Only one authentication method can be used, auth object and username/password are mutually exclusive")
        if self._auth and self.token:
            raise ValueError("Only one authentication method can be used, auth object and token are mutually exclusive")
        if self._auth and (self.client_id or self.client_secret or self.oidc_provider_url):
            raise ValueError(
                "Only one authentication method can be used, auth object and OIDC auth are mutually exclusive")

        if self.token and (self.client_id or self.client_secret or self.oidc_provider_url):
            raise ValueError("Only one authentication method can be used, token and OIDC auth are mutually exclusive")

        if self.token and (self.username or self.password):
            raise ValueError(
                "Only one authentication method can be used, token and username/password are mutually exclusive")

        if (self.username or self.password) and (self.client_id or self.client_secret or self.oidc_provider_url):
            raise ValueError("Only one authentication method can be used, username/password and "
                             "OIDC auth are mutually exclusive")

        if self._auth:
            return self._auth
        # OIDC authentication
        if self.client_id:
            self._get_oidc_token()
            return generate_auth(token=self.token)
        # basic or static token authentication
        elif self.username and self.password:
            return generate_auth(self.username, self.password)

        # static token auth
        elif self.token:
            return generate_auth(token=self.token)
        else:
            return None

    def __repr__(self):

        return f"<FHIRServer api_address={self.api_address}, auth={self.auth}, headers={self.headers}>"


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
    # Static token auth
    token = os.getenv("FHIR_TOKEN")
    # oauth2/oidc authentication
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    oidc_provider_url = os.getenv("OIDC_PROVIDER_URL")

    if username and token:
        raise EnvironmentError("Conflicting auth information, bother username and token present.")
    if username and client_id:
        raise EnvironmentError("Conflicting auth information, bother username and client id present")
    if token and client_id:
        raise EnvironmentError("Conflicting auth information, bother static token and client id present")

    if username:
        password = os.getenv("FHIR_PW")
        if not password:
            raise EnvironmentError(f"No password specified for user: {username}")
        else:
            print(f"Basic auth environment info found -> ({username}:******)")
            return username, password
    if token:
        print("Found static auth token")
        return token

    if client_id and not client_secret:
        raise EnvironmentError("Insufficient auth information, client id specified but no client secret found.")

    if (client_id and client_secret) and not oidc_provider_url:
        raise EnvironmentError("Insufficient auth information, client id and secret "
                               "specified but no provider URL found")
    if client_id and client_secret and oidc_provider_url:
        print(f"Found OIDC auth configuration for client <{client_id}> with provider {oidc_provider_url}")
        return client_id, client_secret, oidc_provider_url


