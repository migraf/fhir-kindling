from typing import List

from fhir.resources.bundle import Bundle
from fhir.resources.domainresource import DomainResource
from fhir.resources.molecularsequence import MolecularSequence

from .resource_generator import FhirResourceGenerator


class MolecularSequenceGenerator(FhirResourceGenerator):
    def __init__(self, n: int, resources: List[DomainResource] = None, resource_type: DomainResource = None,
                 fhir_server: str = None, fhir_user: str = None, fhir_pw: str = None, fhir_token: str = None,
                 fhir_server_type: str = None,
                 sequence_file: str = None,
                 ):
        super().__init__(n, resources, resource_type, fhir_server, fhir_user, fhir_pw, fhir_token, fhir_server_type)
        self.sequence_file = sequence_file


    def generate(self, upload: bool = False, out_dir: str = None):
        super().generate(upload, out_dir)
        self.resources = self._generate()

    def _generate(self):
        pass

    def _load_sequence_file(self, path: str):
        pass

    def make_bundle(self) -> Bundle:
        return super().make_bundle()


if __name__ == '__main__':
    sequence_file = "../examples/hiv_sequences/sequences_1.txt"
    ms_generator = MolecularSequenceGenerator()
