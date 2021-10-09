from typing import Union

from fhir.resources.resource import Resource
import requests


class FHIRQuery:

    def __init__(self, base_url: str, resource: Union[Resource, str] = None,
                 auth: requests.auth.AuthBase = None):
        self.base_url = base_url
        self.resource = resource
        self.auth = auth

        self.session = requests.Session()

        if isinstance(resource, str):
            # todo load pydantic model class
            pass

    def where(self):
        # todo evaluate arbitrary number of expressions based on fields of the resource and query values
        pass

    def include(self):
        pass

    def has(self):
        pass

    def all(self):
        # todo execute the pre built query string and return all resources that match the query
        pass

    def limit(self, n: int):
        # todo return the first n resources that fit the query
        pass

    def first(self):
        # todo return the first resources that fits the query
        pass