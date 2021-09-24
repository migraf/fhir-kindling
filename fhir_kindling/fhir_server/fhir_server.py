from fhir.resources import FHIRAbstractModel
from fhir_kindling.fhir_query import FHIRQuery


class FhirServer:

    def __init__(self, api_address: str, username: str = None, password: str = None, token: str = None):
        self.api_address = api_address
        self.username = username
        self.password = password
        self.token = token

    def query(self, resource: FHIRAbstractModel = None, query_string: str = None):
        pass

    def health_check(self):
        pass

    def meta_data(self):
        pass

    @staticmethod
    def _headers():
        return {"Content-Type": "application/fhir+json"}
