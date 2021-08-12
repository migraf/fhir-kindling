import pprint
from typing import List, Union
from fhir.resources.domainresource import DomainResource
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
import os

from train_lib.fhir import PHTFhirClient


class FhirResourceGenerator:

    def __init__(self, n: int, resources: List[DomainResource] = None,
                 resource_type: DomainResource = None,
                 fhir_server: str = None, fhir_user: str = None, fhir_pw: str = None, fhir_token: str = None):
        self.fhir_token = fhir_token if fhir_token else os.getenv("FHIR_TOKEN")
        self.fhir_pw = fhir_pw if fhir_pw else os.getenv("FHIR_PW")
        self.fhir_user = fhir_user if fhir_user else os.getenv("FHIR_USER")
        self.fhir_server = fhir_server if fhir_server else os.getenv("FHIR_SERVER_URL")
        self.n = n
        self.resource_type = resource_type
        self.resources = resources

        if self.fhir_server:
            self.fhir_client = PHTFhirClient(server_url=self.fhir_server, username=self.fhir_user,
                                             password=self.fhir_pw, token=self.fhir_token)

    def generate(self, upload: bool = False):
        if upload:
            bundle = self.make_bundle()
            self.fhir_client.upload_resource_or_bundle(bundle=bundle)

    def make_bundle(self) -> Bundle:
        entries = self._generate_bundle_entries()
        bundle_data = {
            "type": "transaction",
            "entry": entries
        }
        bundle = Bundle(**bundle_data)
        return bundle

    def _generate_bundle_entries(self):
        entries = []
        for resource in self.resources:
            bundle_entry_dict = {
                "resource": resource,
                "request": BundleEntryRequest(**{"method": "POST", "url": self.resource_type.get_resource_type()})
            }
            entry = BundleEntry(**bundle_entry_dict)
            entries.append(entry)
        return entries

    def display_schema(self):
        pprint.pprint(self.resource_type.schema())
