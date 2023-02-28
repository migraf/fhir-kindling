import os
import re
from typing import List, OrderedDict, Union

import fhir.resources
import httpx
from authlib.integrations.httpx_client import OAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
from authlib.oauth2.rfc7523 import ClientSecretJWT
from fhir.resources import FHIRAbstractModel, construct_fhir_element
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.capabilitystatement import CapabilityStatement
from fhir.resources.fhirresourcemodel import FHIRResourceModel
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource
from networkx import DiGraph
from tqdm import tqdm

from fhir_kindling.fhir_query import FhirQueryAsync, FhirQuerySync
from fhir_kindling.fhir_query.query_parameters import FhirQueryParameters
from fhir_kindling.fhir_query.query_response import QueryResponse
from fhir_kindling.fhir_server.auth import BearerAuth, auth_info_from_env
from fhir_kindling.fhir_server.server_responses import (
    BundleCreateResponse,
    ResourceCreateResponse,
    TransferResponse,
)
from fhir_kindling.fhir_server.summary import ServerSummary, create_server_summary
from fhir_kindling.fhir_server.transactions import (
    TransactionMethod,
    TransactionType,
    make_transaction_bundle,
)
from fhir_kindling.fhir_server.transfer import reference_graph
from fhir_kindling.serde.json import json_dict
from fhir_kindling.util.references import check_missing_references
from fhir_kindling.util.resources import valid_resource_name


class FhirServer:
    def __init__(
        self,
        api_address: str,
        username: str = None,
        password: str = None,
        token: str = None,
        client_id: str = None,
        client_secret: str = None,
        oidc_provider_url: str = None,
        auth: httpx.Auth = None,
        headers: dict = None,
        proxies: Union[dict, str] = None,
        timeout: int = None,
        fhir_server_type: str = "hapi",
    ):
        """
        Initialize a FHIR server connection
        Args:
            api_address: the base endpoint of the fhir server REST API
            username: username for basic auth
            password: password for basic auth
            token: token for static token auth
            client_id: client id for oauth2
            client_secret: client secret for oauth2
            oidc_provider_url: provider url for oauth2
            auth: optional auth object to authenticate against a server
            headers: optional additional headers to be added to the session
            proxies: optional proxies to be added to the session
            timeout: optional timeout for the session default is None
            fhir_server_type: type of fhir server (hapi, blaze, etc.)
        """

        # server definition values
        self.fhir_server_type = fhir_server_type
        self.api_address = self._validate_api_address(api_address)
        self._meta_data = None

        # possible basic auth class vars
        self.username = username
        self.password = password

        # static token
        self.token = token

        # oauth2 auth vars
        self.client_id = client_id
        self.client_secret = client_secret
        self.oidc_provider_url = oidc_provider_url
        self.oauth_token: OAuth2Token = None

        self._auth = auth
        self._headers = headers
        self._proxies = proxies
        self._timeout = timeout

    @classmethod
    def from_env(cls, no_auth: bool = False) -> "FhirServer":
        api_address = _api_address_from_env()
        server_type = os.getenv("FHIR_SERVER_TYPE")

        if no_auth:
            return FhirServer(api_address=api_address, fhir_server_type=server_type)
        else:
            env_auth = auth_info_from_env()
            # static token
            if isinstance(env_auth, str):
                return cls(
                    api_address=api_address,
                    token=env_auth,
                    fhir_server_type=server_type,
                )
            # username and password
            elif isinstance(env_auth, tuple) and len(env_auth) == 2:
                return cls(
                    api_address=api_address,
                    username=env_auth[0],
                    password=env_auth[1],
                    fhir_server_type=server_type,
                )
            # oauth2/oidc
            elif isinstance(env_auth, tuple) and len(env_auth) == 3:
                return cls(
                    api_address=api_address,
                    client_id=env_auth[0],
                    client_secret=env_auth[1],
                    oidc_provider_url=env_auth[2],
                    fhir_server_type=server_type,
                )
            else:
                raise EnvironmentError(
                    "Authentication information could not be loaded from environment"
                )

    def query(
        self,
        resource: Union[Resource, FHIRAbstractModel, str] = None,
        query_string: str = None,
        query_parameters: FhirQueryParameters = None,
        output_format: str = "json",
    ) -> FhirQuerySync:
        """
        Initialize a FHIR query against the server with the given resource, query parameters or query string

        Args:
            output_format: the output format to request from the fhir server (json or xml) defaults to json
            query_string: preformatted query string to execute against the servers REST API
            query_parameters: optionally pass in a query parameters object to use for the query
            resource: the FHIR resource to query from the server

        Returns: a FhirQuerySync object that can be further modified with filters and conditions before being executed
        against the server
        """

        self._validate_query_input(resource, query_parameters, query_string)

        if resource:
            if isinstance(resource, str):
                resource = valid_resource_name(resource)
            # validate the given resource name
            return FhirQuerySync(
                base_url=self.api_address,
                resource=resource,
                auth=self.auth,
                output_format=output_format,
                proxies=self._proxies,
                headers=self._headers,
            )
        elif query_string:
            return self.raw_query(query_string, output_format)

        else:
            return FhirQuerySync(
                base_url=self.api_address,
                auth=self.auth,
                query_parameters=query_parameters,
                output_format=output_format,
                proxies=self._proxies,
                headers=self._headers,
            )

    def query_async(
        self,
        resource: Union[Resource, FHIRAbstractModel, str] = None,
        query_string: str = None,
        query_parameters: FhirQueryParameters = None,
        output_format: str = "json",
    ) -> FhirQueryAsync:
        """
        Initialize a FHIR query against the server with the given resource, query parameters or query string

        Args:
            output_format: the output format to request from the fhir server (json or xml) defaults to json
            query_string: preformatted query string to execute against the servers REST API
            query_parameters: optionally pass in a query parameters object to use for the query
            resource: the FHIR resource to query from the server

        Returns: a FhirQueryAsync object that can be further modified with filters and conditions before being executed
        against the server
        """

        self._validate_query_input(resource, query_parameters, query_string)

        if resource:
            return FhirQueryAsync(
                base_url=self.api_address,
                resource=resource,
                auth=self.auth,
                output_format=output_format,
                proxies=self._proxies,
            )
        elif query_string:
            query_parameters = FhirQueryParameters.from_query_string(query_string)
            query = FhirQueryAsync(
                self.api_address,
                resource=query_parameters.resource,
                query_parameters=query_parameters,
                output_format=output_format,
                proxies=self._proxies,
            )
            return query

        else:
            return FhirQueryAsync(
                base_url=self.api_address,
                auth=self.auth,
                query_parameters=query_parameters,
                output_format=output_format,
                proxies=self._proxies,
            )

    def raw_query(
        self, query_string: str, output_format: str = "json"
    ) -> FhirQuerySync:
        """
        Execute a raw query string against the server

        Args:
            query_string:
            output_format:
        Returns:

        """

        query_parameters = FhirQueryParameters.from_query_string(query_string)
        query = FhirQuerySync(
            base_url=self.api_address,
            query_parameters=query_parameters,
            output_format=output_format,
            auth=self.auth,
            proxies=self._proxies,
            headers=self._headers,
        )
        return query

    def raw_query_async(
        self, query_string: str, output_format: str = "json"
    ) -> FhirQueryAsync:
        """
        Asynchronously Execute a raw query string against the server

        Args:
            query_string: query string defining the query to execute
            output_format: the output format to request from the fhir server (json or xml) defaults to json
        Returns:
            a FhirQueryAsync object that can be further modified with filters and conditions before being executed
            against the server

        """

        query_parameters = FhirQueryParameters.from_query_string(query_string)
        query = FhirQueryAsync(
            base_url=self.api_address,
            resource=query_parameters.resource,
            query_parameters=query_parameters,
            output_format=output_format,
            auth=self.auth,
            proxies=self._proxies,
        )
        return query

    def get(self, reference: Union[str, Reference]) -> FHIRAbstractModel:
        """
        Get a resource from the server specified by the given reference {ResourceType}/{id}

        Args:
            reference: reference to the resource, either a Reference object or a string of the form {ResourceType}/{id}

        Returns:
            the resource from the server specified by the reference

        """
        if isinstance(reference, Reference):
            reference = reference.reference
        with self._sync_client() as client:
            r = client.get(f"{self.api_address}/{reference}")
        r.raise_for_status()
        resource_dict = r.json()
        resource = construct_fhir_element(resource_dict["resourceType"], resource_dict)
        return resource

    async def get_async(self, reference: Union[str, Reference]) -> FHIRAbstractModel:
        """
        Asynchronously get a resource from the server specified by the given reference {ResourceType}/{id}

        Args:
            reference: reference to the resource, either a Reference object or a string of the form {ResourceType}/{id}

        Returns:
            the resource from the server specified by the reference

        """
        if isinstance(reference, Reference):
            reference = reference.reference
        async with self._async_client() as client:
            r = await client.get(f"{self.api_address}/{reference}")
            r.raise_for_status()
        resource_dict = r.json()
        resource = construct_fhir_element(resource_dict["resourceType"], resource_dict)
        return resource

    def get_many(
        self, references: List[Union[str, Reference]]
    ) -> List[FHIRAbstractModel]:
        """
        Get a list of resources from the server specified by the given references

        Args:
            references: list of references to the resources, either a Reference object or a string of the form
                `{ResourceType}/{id}`

        Returns:
            list of resources corresponding to the references

        """
        str_references = [
            reference if isinstance(reference, str) else reference.reference
            for reference in references
        ]

        get_many_transaction = make_transaction_bundle(
            method=TransactionMethod.GET,
            transaction_type=TransactionType.BATCH,
            references=str_references,
        )
        with self._sync_client() as client:
            r = client.post(self.api_address, json=json_dict(get_many_transaction))
            r.raise_for_status()
        entries = r.json()["entry"]
        resources = [
            construct_fhir_element(entry["resource"]["resourceType"], entry["resource"])
            for entry in entries
        ]

        return resources

    async def get_many_async(
        self, references: List[Union[str, Reference]]
    ) -> List[FHIRAbstractModel]:
        """
        Asynchronously get a list of resources from the server specified by the given references

        Args:
            references: list of references to the resources, either a Reference object or a string of the form
                `{ResourceType}/{id}`

        Returns:
            list of resources corresponding to the references

        """
        str_references = [
            reference if isinstance(reference, str) else reference.reference
            for reference in references
        ]
        get_many_transaction = make_transaction_bundle(
            method=TransactionMethod.GET,
            transaction_type=TransactionType.BATCH,
            references=str_references,
        )

        async with self._async_client() as client:
            response = await client.post(
                self.api_address, json=get_many_transaction.dict(exclude_none=True)
            )

        # construct the list of resources from the server response
        resources = [
            construct_fhir_element(entry["resource"]["resourceType"], entry["resource"])
            for entry in response.json()["entry"]
        ]
        return resources

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

        return ResourceCreateResponse(
            server_response_dict=dict(response.headers), resource=resource
        )

    async def add_async(
        self, resource: Union[Resource, dict]
    ) -> ResourceCreateResponse:
        """
        Asynchronously upload a resource to the server

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
        response = await self._upload_resource_async(resource)
        return ResourceCreateResponse(
            server_response_dict=dict(response.headers), resource=resource
        )

    def add_all(
        self,
        resources: List[Union[Resource, dict]],
        batch_size: int = 5000,
        display: bool = True,
    ) -> BundleCreateResponse:
        """
        Upload a list of resources to the server, after packaging them into a bundle
        Args:
            resources: list of resources to upload to the server, either dictionary or FHIR resource objects
            batch_size: maximum number of resources to upload in one bundle
            display: whether to display a progress bar when the upload is batched

        Returns: Bundle create response from the fhir server

        """
        response = None
        if len(resources) > batch_size:
            # split the list of resources into batches of size batch_size
            batches = [
                resources[i : i + batch_size]
                for i in range(0, len(resources), batch_size)
            ]

            p_bar = tqdm(batches, disable=not display)
            for i, batch in enumerate(p_bar):
                p_bar.set_description(
                    f"Uploading Batch {i + 1}/{len(batches)}, n={len(batch)}"
                )
                bundle = make_transaction_bundle(
                    method=TransactionMethod.POST, resources=batch
                )
                if not response:
                    response = self._upload_bundle(bundle)
                else:
                    add_response = self._upload_bundle(bundle)
                    response.create_responses.extend(add_response.create_responses)
        else:
            bundle = make_transaction_bundle(
                method=TransactionMethod.POST, resources=resources
            )
            response = self._upload_bundle(bundle)
        return response

    async def add_all_async(
        self,
        resources: List[Union[Resource, dict]],
        batch_size: int = 5000,
        display: bool = True,
    ) -> BundleCreateResponse:
        """
        Asynchronously upload a list of resources to the server, after packaging them into a bundle
        Args:
            resources: list of resources to upload to the server, either dictionary or FHIR resource objects
            batch_size: maximum number of resources to upload in one bundle
            display: whether to display a progress bar when the upload is batched

        Returns: Bundle create response from the fhir server

        """
        response = None
        if len(resources) > batch_size:
            # split the list of resources into batches of size batch_size
            batches = [
                resources[i : i + batch_size]
                for i in range(0, len(resources), batch_size)
            ]
            p_bar = tqdm(batches, disable=not display)
            for i, batch in enumerate(p_bar):
                p_bar.set_description(
                    f"Uploading Batch {i + 1}/{len(batches)}, n={len(batch)}"
                )

                # create a bundle from the batch of resources
                bundle = make_transaction_bundle(
                    method=TransactionMethod.POST, resources=batch
                )
                if not response:
                    response = await self._upload_bundle_async(bundle)
                else:
                    add_response = await self._upload_bundle_async(bundle)
                    response.create_responses.extend(add_response.create_responses)
        else:
            # create a bundle from the list of resources
            bundle = make_transaction_bundle(
                method=TransactionMethod.POST, resources=resources
            )
            response = await self._upload_bundle_async(bundle)
        return response

    def add_bundle(
        self, bundle: Union[Bundle, dict, str], validate: bool = True
    ) -> BundleCreateResponse:
        """
        Upload a bundle to the server
        :param bundle: str, dict or Bundle object to upload to the server
        :param validate: whether to validate the entries in the bundle
        :return: BundleCreateResponse from the fhir server containing the server assigned ids of the resources in
        the bundle
        """
        # create bundle and validate it
        if isinstance(bundle, dict):
            bundle = Bundle(**bundle)
        elif isinstance(bundle, str):
            bundle = Bundle.parse_raw(bundle)
        else:
            bundle = Bundle.validate(bundle)
        # check that all entries are bundle requests with methods post/put
        if validate:
            self._validate_upload_bundle_entries(bundle.entry)

        create_response = self._upload_bundle(bundle)
        return create_response

    async def add_bundle_async(
        self, bundle: Union[Bundle, dict, str], validate_entries: bool = True
    ) -> BundleCreateResponse:
        """
        Asynchronously upload a bundle to the server
        :param bundle: str, dict or Bundle object to upload to the server
        :param validate_entries: whether to validate the entries in the bundle
        :return: BundleCreateResponse from the fhir server containing the server assigned ids of the resources in
        the bundle
        """
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

        transaction_response = await self._upload_bundle_async(bundle)
        return transaction_response

    def update(self, resources: List[Union[FHIRResourceModel, dict]]) -> dict:
        """
        Update a list of resources that exist on the server
        Args:
            resources: List of updated resources coming to send to the server

        Returns: Bundle update response from the fhir server

        """

        update_bundle = make_transaction_bundle(
            method=TransactionMethod.PUT, resources=resources
        )
        with self._sync_client() as client:
            r = client.post(self.api_address, json=json_dict(update_bundle))
            r.raise_for_status()
        return r.json()

    async def update_async(self, resources: List[Union[FHIRResourceModel, dict]]):
        update_bundle = make_transaction_bundle(
            method=TransactionMethod.PUT, resources=resources
        )

        async with self._async_client() as client:
            r = await client.post(self.api_address, json=json_dict(update_bundle))
            r.raise_for_status()
        return r.json()

    def delete(
        self,
        resources: List[Union[FHIRResourceModel, dict]] = None,
        references: List[Union[str, Reference]] = None,
        query: FhirQuerySync = None,
    ):
        """
        Delete resources from the server. Either resources, references or a query must be specified.
        Args:
            resources: Resources coming from the server containing an id to delete
            references: references {Resource}/{id} to delete
            query: query to use to find resources to delete

        Returns:

        """

        self._validate_delete_args(query, references, resources)

        # if a query is specified, get the resources to delete
        if query:
            resp = query.all()
            resources = resp.resource_list
        delete_bundle = make_transaction_bundle(
            method=TransactionMethod.DELETE,
            resources=resources,
            references=references,
        )

        with self._sync_client() as client:
            r = client.post(self.api_address, json=json_dict(delete_bundle))
            r.raise_for_status()

    async def delete_async(
        self,
        resources: List[Union[FHIRResourceModel, dict]] = None,
        references: List[Union[str, Reference]] = None,
        query: FhirQueryAsync = None,
    ):
        """
        Asynchronously delete resources from the server. Either resources, references or a query must be specified.
        Args:
            resources: Resources coming from the server containing an id to delete
            references: references {Resource}/{id} to delete
            query: query to use to find resources to delete

        Returns:

        """
        self._validate_delete_args(query, references, resources)
        # if a query is specified, get the resources to delete
        if query:
            resp = await query.all()
            resources = resp.resource_list

        delete_bundle = make_transaction_bundle(
            method=TransactionMethod.DELETE,
            resources=resources,
            references=references,
        )

        async with self._async_client() as client:
            r = await client.post(self.api_address, json=json_dict(delete_bundle))
            r.raise_for_status()

    def transfer(
        self,
        target_server: "FhirServer",
        query_params: FhirQueryParameters = None,
        query_result: QueryResponse = None,
    ) -> TransferResponse:
        """
        Transfer resources from this server to another server while using server assigned ids and keeping referential
        integrity.
        Args:
            target_server: FhirServer to transfer to
            query_params: FhirQueryParameters to use to find resources to transfer
            query_result: results of the initial query against the server

        Returns: Transfer response for the transfer of the query result to the target server

        """
        # get all the referenced resources missing in the list from the source server
        if query_result and query_params:
            raise ValueError("Cannot specify both query and query_result")
        # if query parameters are given execute the query against the server
        elif query_params:
            query_result = self.query(query_parameters=query_params).all()
        # find missing references
        missing_references = check_missing_references(query_result.resources)
        if missing_references:
            resources = self._get_missing_resources(query_result.resources)
        else:
            resources = query_result.resources
        # transfer the resources keeping server assigned ids and referential integrity
        response = self._transfer_resources(
            target_server, resources, query_result.query_params
        )

        return response

    def summary(self, display: bool = True) -> ServerSummary:
        """
        Create a summary for the server. Contains resource counts for all resources available on the server.
        Args:
            display: whether to display a progress bar
        Returns:

        """
        summary = create_server_summary(self, self.rest_resources, display)
        return summary

    @property
    def capabilities(self) -> CapabilityStatement:
        if not self._meta_data:
            self._get_meta_data()
        return CapabilityStatement(**self._meta_data)

    @property
    def rest_resources(self) -> List[str]:
        return [capa.type for capa in self.capabilities.rest[0].resource]

    @property
    def headers(self):
        headers = {"Content-Type": "application/fhir+json"}
        if self._headers:
            headers.update(self._headers)
        return headers

    @property
    def auth(self):
        if self._auth:
            return self._auth
        elif self.username and self.password:
            return httpx.BasicAuth(username=self.username, password=self.password)
        elif self.token:
            return BearerAuth(self.token)

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
            r"^(?:http|ftp)s?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
            r"localhost|"  # localhost...
            r"[A-Za-z0-9_-]*|"  # single word with hyphen/underscore for docker
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        if re.match(regex, api_address):
            if api_address[-1] == "/":
                api_address = api_address[:-1]
            return api_address

        else:
            raise ValueError(f"Malformed API URL: {api_address}")

    @staticmethod
    def _validate_delete_args(query, references, resources):
        if query and (resources or references):
            raise ValueError("Cannot specify both query and resources/references")
        if not (query or resources or references):
            raise ValueError("Must specify either query or resources/references")

    @staticmethod
    def _validate_upload_bundle_entries(entries: List[BundleEntry]):
        for i, entry in enumerate(entries):
            if entry.request.method.lower() not in ["post", "put"]:
                raise ValueError(f"Entry {i}:  method is not in [post, put]")

    def _upload_bundle(self, bundle: Bundle) -> BundleCreateResponse:
        """
        Upload a bundle to the server
        Args:
            bundle: transaction bundle to upload to the server

        Returns:
            BundleCreateResponse with the server assigned ids

        """
        with self._sync_client() as client:

            r = client.post(url=self.api_address, json=json_dict(bundle))
            try:
                r.raise_for_status()
            except Exception as e:
                print(r.text)
                raise e
        bundle_response = BundleCreateResponse(r, bundle)
        return bundle_response

    async def _upload_bundle_async(self, bundle: Bundle) -> BundleCreateResponse:
        """
        Asynchronously upload a bundle to the server
        Args:
            bundle: Bundle to upload to the server

        Returns:
            BundleCreateResponse with the server assigned ids
        """
        async with self._async_client() as client:
            r = await client.post(url=self.api_address, json=json_dict(bundle))
            try:
                r.raise_for_status()
            except Exception as e:
                print(r.text)
                raise e
        bundle_response = BundleCreateResponse(r, bundle)
        return bundle_response

    def _upload_resource(self, resource: Resource) -> httpx.Response:
        """
        Upload a resource to the server
        Args:
            resource: Fhir resource to upload

        Returns:
            httpx.Response from the server
        """
        url = self.api_address + "/" + resource.get_resource_type()
        with self._sync_client() as client:
            r = client.post(url=url, json=json_dict(resource))
            try:
                r.raise_for_status()
            except Exception as e:
                print(r.text)
                raise e
        return r

    async def _upload_resource_async(self, resource: Resource) -> httpx.Response:
        """
        Asynchronously upload a resource to the server
        Args:
            resource: Fhir resource to upload

        Returns:
            httpx.Response from the server
        """
        url = self.api_address + "/" + resource.get_resource_type()
        async with self._async_client() as client:
            r = await client.post(url=url, json=json_dict(resource))
            try:
                r.raise_for_status()
            except Exception as e:
                print(r.text)
                raise e
        return r

    def _get_meta_data(self):
        url = self.api_address + "/metadata"
        with self._sync_client() as client:
            r = client.get(url)
            try:
                r.raise_for_status()
            except Exception as e:
                print(r.text)
                raise e
        response = r.json()
        self._meta_data = response

    def _sync_client(self) -> httpx.Client:
        client = httpx.Client(
            headers=self.headers,
            auth=self.auth,
            proxies=self._proxies,
            timeout=self._timeout,
        )
        return client

    def _async_client(self) -> httpx.AsyncClient:
        client = httpx.AsyncClient(
            headers=self.headers,
            auth=self.auth,
            proxies=self._proxies,
            timeout=self._timeout,
        )
        return client

    def _get_oidc_token(self):
        # get a new token if it is expired or not yet set
        if not self.oauth_token or self.oauth_token.is_expired():
            client = OAuth2Client(
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_endpoint_auth_method="client_secret_jwt",
            )
            client.register_client_auth_method(ClientSecretJWT(self.oidc_provider_url))
            token = client.fetch_token(self.oidc_provider_url)
            self.token = token["access_token"]
            self.oauth_token = token

    def _get_missing_resources(
        self, resources: List[Union[Resource, FHIRAbstractModel]]
    ):
        missing = check_missing_references(resources)

        while missing:
            missing_resources = self.get_many(missing)
            resources.extend(missing_resources)
            missing = check_missing_references(resources)

        return resources

    def _transfer_resources(
        self,
        target_server: "FhirServer",
        resources: List[FHIRAbstractModel],
        params: FhirQueryParameters = None,
    ) -> TransferResponse:
        graph = reference_graph(resources)
        print(graph)
        create_responses = self._resolve_reference_graph(graph, target_server)

        return TransferResponse(
            origin_server=self.api_address,
            destination_server=target_server.api_address,
            create_responses=create_responses,
            query_parameters=params,
        )

    def _resolve_reference_graph(
        self, graph: DiGraph, server: "FhirServer"
    ) -> List[ResourceCreateResponse]:
        create_responses = []
        nodes = graph.nodes
        while len(nodes) > 0:
            # find the nodes without references and add them to the target server
            top_nodes = [
                node for node in nodes if len(list(graph.predecessors(node))) == 0
            ]
            resources = [graph.nodes[node]["resource"] for node in top_nodes]
            parsed_resources = []
            for r in resources:
                if isinstance(r, OrderedDict):
                    resource_dict = dict(r)
                    resource_type = resource_dict.get(
                        "resourceType", resource_dict.get("resource_type")
                    )
                    parsed_resources.append(
                        construct_fhir_element(resource_type, resource_dict)
                    )
                    parsed_resources.append(r)
                elif isinstance(r, FHIRAbstractModel):
                    parsed_resources.append(r)
                else:
                    print(type(r))
            add_response = server.add_all(parsed_resources)
            # update dependant nodes in the graph with the obtained references
            self._update_graph_references(graph, top_nodes, add_response.references)
            create_responses.extend(add_response.create_responses)
            # remove processed nodes from the graph
            graph.remove_nodes_from(top_nodes)
            nodes = graph.nodes
        return create_responses

    @staticmethod
    def _update_graph_references(graph: DiGraph, nodes, references: List[str]) -> None:
        """
        Update the graph with the obtained references
        Args:
            graph: reference graph to update
            nodes: the unreferenced nodes
            references: references obtained from the server after submitting the resources contained in the unreferenced
                nodes

        Returns:

        """
        for node, reference in zip(nodes, references):
            # Get the successors of the node that was just processed
            successors = graph.successors(node)
            for successor in successors:
                field = graph[node][successor]["field"]
                list_field = graph[node][successor]["list_field"]
                # if the reference field is a list of references, update the corresponding list item
                if list_field:
                    # Find the item that references the node
                    reference_list = graph.nodes[successor]["resource"].dict()[field]
                    reference_item = next(
                        (
                            item
                            for item in reference_list
                            if item.get("reference") == str(node)
                        ),
                        None,
                    )
                    # if the item is found replace it with the obtained reference
                    if reference_item:
                        index = reference_list.index(reference_item)
                        resource = graph.nodes[successor]["resource"].dict()
                        resource[field][index] = reference
                        graph.nodes[successor]["resource"] = resource

                # update the reference field in the dependant resource
                else:
                    if not isinstance(graph.nodes[successor]["resource"], dict):
                        resource = graph.nodes[successor]["resource"].dict()
                        resource[field] = reference
                        graph.nodes[successor]["resource"] = resource
                    else:
                        graph.nodes[successor]["resource"][field] = reference

    @staticmethod
    def _validate_query_input(
        resource: str, query_parameters: FhirQueryParameters, query_string: str
    ):
        if resource and query_parameters:
            raise ValueError("Cannot specify both a resource and query parameters")
        if query_string and query_parameters:
            raise ValueError("Cannot specify both a query string and query parameters")
        if resource and query_string:
            raise ValueError("Cannot specify both a resource and query string")
        if not resource and not query_string and not query_parameters:
            raise ValueError(
                "Must specify either a resource, query string or query parameters"
            )

    def __repr__(self):
        return f"FhirServer(api_address={self.api_address})"


def _api_address_from_env() -> str:
    # load FHIR_API_URL
    api_url = os.getenv("FHIR_API_URL")
    if not api_url:
        api_url = os.getenv("FHIR_SERVER_URL")
    if not api_url:
        raise EnvironmentError("No FHIR api address specified")
    return FhirServer._validate_api_address(api_url)
