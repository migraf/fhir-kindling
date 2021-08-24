from typing import List

from fhir.resources.bundle import Bundle
from fhir.resources.domainresource import DomainResource

from fhir_kindling.resource_generator import FhirResourceGenerator

class FHIRMediaGenerator(FhirResourceGenerator):
    def __init__(self, n: int, resources: List[DomainResource] = None, resource_type: DomainResource = None,
                 fhir_server: str = None, fhir_user: str = None, fhir_pw: str = None, fhir_token: str = None,
                 fhir_server_type: str = None):
        super().__init__(n, resources, resource_type, fhir_server, fhir_user, fhir_pw, fhir_token, fhir_server_type)

    def generate(self, upload: bool = False, out_dir: str = None):
        super().generate(upload, out_dir)

    def make_bundle(self) -> Bundle:
        return super().make_bundle()
