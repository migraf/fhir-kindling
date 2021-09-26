import json
from typing import List, Union

import pandas as pd
import requests
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle
from fhir.resources.capabilitystatement import CapabilityStatement

from fhir_kindling.fhir_query import FHIRQuery
from fhir_kindling.auth import generate_auth
from fhir_kindling.fhir_query.query_functions import query_with_string
from fhir_kindling.serde import flatten_bundle
from fhir_kindling.upload import upload_bundle

import re


class FhirServer:

    def __init__(self, api_address: str, username: str = None, password: str = None, token: str = None,
                 fhir_server_type: str = "hapi"):
        self.fhir_server_type = fhir_server_type
        self.api_address = self._validate_api_address(api_address)
        self.username = username
        self.password = password
        self.token = token
        self._meta_data = None

    def query(self, resource: Resource = None) -> FHIRQuery:
        pass

    def raw_query(self, query_string: str, output_format: str = "json", limit: int = None, count: int = 2000):
        valid_query_string = self._validate_query_string(query_string)

        response = query_with_string(valid_query_string, fhir_server_url=self.api_address,
                                     auth=self._auth, headers=self._headers, limit=limit, count=count)

        return self._format_output(response, output_format)

    def add(self, resource: Resource):
        # todo
        pass

    def add_all(self, resources: List[Resource]):
        # todo
        pass

    def add_bundle(self, bundle: Union[Bundle, dict, str]):
        # todo
        if isinstance(bundle, dict):
            bundle = Bundle(**bundle)

        elif isinstance(bundle, str):
            bundle = Bundle(**json.loads(bundle))

    def _format_output(self, bundle_response: dict, output_format: str) -> Union[dict, pd.DataFrame, Bundle]:
        if output_format in {"json", "raw"}:
            return bundle_response
        elif output_format == "parsed":
            return Bundle(**bundle_response)
        elif output_format == "df":
            return flatten_bundle(bundle_response)

    def _get_meta_data(self):
        url = self.api_address + "/metadata"
        r = requests.get(url, auth=self._auth, headers=self._headers)
        r.raise_for_status()
        response = r.json()
        self._meta_data = response

    @property
    def capabilities(self) -> CapabilityStatement:
        if not self._meta_data:
            self._get_meta_data()
        return CapabilityStatement(**self._meta_data)

    @property
    def _auth(self):
        return generate_auth(self.username, self.password, self.token)

    @property
    def _headers(self):
        return {"Content-Type": "application/fhir+json"}

    def _validate_query_string(self, query_string_input: str) -> str:
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
