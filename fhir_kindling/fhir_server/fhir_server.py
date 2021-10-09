import datetime
import json
import os
from typing import List, Union

import pandas as pd
import requests
from requests import Response
import requests.auth
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle
from fhir.resources.capabilitystatement import CapabilityStatement
from requests_oauthlib import OAuth2Session

from fhir_kindling.fhir_query import FHIRQuery
from fhir_kindling.fhir_server.auth import generate_auth
from fhir_kindling.fhir_query.query_functions import query_with_string
from fhir_kindling.serde import flatten_bundle
from oauthlib.oauth2 import BackendApplicationClient
from dotenv import load_dotenv, find_dotenv
import pendulum

import re


class FhirServer:

    def __init__(self, api_address: str, username: str = None, password: str = None, token: str = None,
                 client_id: str = None, client_secret: str = None, oidc_provider_url: str = None,
                 fhir_server_type: str = "hapi"):
        self.fhir_server_type = fhir_server_type
        self.api_address = self._validate_api_address(api_address)
        self.username = username
        self.password = password
        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
        self.oidc_provider_url = oidc_provider_url
        self._meta_data = None
        self.token_expiration = None

    def query(self, resource: Resource = None) -> FHIRQuery:
        return FHIRQuery(self.api_address, resource, auth=self.auth)

    def raw_query(self, query_string: str, output_format: str = "json", limit: int = None, count: int = 2000):
        valid_query_string = self._validate_query_string(query_string)

        response = query_with_string(valid_query_string, fhir_server_url=self.api_address,
                                     auth=self.auth, headers=self._headers, limit=limit, count=count)

        return self._format_output(response, output_format)

    def add(self, resource: Union[Resource, dict]) -> dict:

        if isinstance(resource, dict):
            # todo load resource based on dict
            pass
        response = self._upload_resource(resource)
        print(response.headers)
        print(response.text)
        response.raise_for_status()

        return response.json()

    def add_all(self, resources: List[Resource]):
        # todo make bundle from list of resource
        pass

    def add_bundle(self, bundle: Union[Bundle, dict, str]):
        # todo check this
        if isinstance(bundle, dict):
            bundle = Bundle(**bundle)

        elif isinstance(bundle, str):
            bundle = Bundle(**json.loads(bundle))

        url = self.api_address
        r = requests.post(url, headers=self._headers, auth=self._auth, json=bundle.dict())

        r.raise_for_status()

        return r.json()

    def _format_output(self, bundle_response: dict, output_format: str) -> Union[dict, pd.DataFrame, Bundle]:
        pass

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
        r = requests.get(url, auth=self.auth, headers=self._headers)
        r.raise_for_status()
        response = r.json()
        self._meta_data = response

    def _setup(self):
        pass

    @property
    def capabilities(self) -> CapabilityStatement:
        if not self._meta_data:
            self._get_meta_data()
        return CapabilityStatement(**self._meta_data)

    @property
    def auth(self) -> Union[requests.auth.AuthBase]:
        # OIDC authentication
        if self.client_id:

            token = self._get_oidc_token()
            print(token)
            return generate_auth(token=token)
        else:
            return generate_auth(self.username, self.password, self.token)

    def _get_oidc_token(self):

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

        return self.token

    @property
    def _headers(self):
        return {"Content-Type": "application/fhir+json"}

    @staticmethod
    def _validate_query_string(query_string_input: str) -> str:
        if query_string_input[0] != "/":
            valid_query = "/" + query_string_input
        else:
            valid_query = query_string_input
        return valid_query

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
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, api_address):
            if api_address[-1] == "/":
                api_address = api_address[:-1]
            return api_address

        else:
            raise ValueError(f"Malformed API URL: {api_address}")


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    server = FhirServer(
        api_address=os.getenv("LOCAL_BLAZE"),
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL")
    )
    print(server.auth)
    print(server.raw_query("/Patient"))
