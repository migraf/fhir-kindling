from typing import List, Union

import requests
from fhir.resources import FHIRAbstractModel
from fhir.resources.bundle import Bundle

from fhir_kindling.fhir_query import FHIRQuery
from fhir_kindling.auth import generate_auth
import re


class FhirServer:

    def __init__(self, api_address: str, username: str = None, password: str = None, token: str = None,
                 fhir_server_type: str = "hapi"):
        self.fhir_server_type = fhir_server_type
        self.api_address = self._validate_api_address(api_address)
        self.username = username
        self.password = password
        self.token = token

    def query(self, resource: FHIRAbstractModel = None, query_string: str = None) -> FHIRQuery:
        pass

    def health_check(self):
        pass

    def meta_data(self):
        url = self.api_address + ""
        r = requests.get(url, auth=self._auth, headers=self._headers)
        r.raise_for_status()
        response = r.json()
        return response

    def add(self, resource: FHIRAbstractModel):
        # todo
        pass

    def add_all(self, resources: List[FHIRAbstractModel]):
        pass

    def add_bundle(self, bundle: Union[Bundle, dict, str]):
        pass

    @property
    def _auth(self):
        return generate_auth(self.username, self.password, self.token)

    @property
    def _headers(self):
        return {"Content-Type": "application/fhir+json"}

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
