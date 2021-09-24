from typing import Union

from fhir.resources import FHIRAbstractModel


class FHIRQuery:

    def __init__(self, base_url: str, resource: Union[FHIRAbstractModel, str] = None, query_string: str = None):
        self.base_url = base_url
        self.resource = resource
        self.query_string = query_string

    def where(self):
        # todo evaluate arbitrary number of expressions based on fields of the resource and query values
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
