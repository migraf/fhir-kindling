import os
from typing import List, Union

from fhir.resources.bundle import Bundle
from fhir.resources.domainresource import DomainResource
from fhir.resources.molecularsequence import MolecularSequence, MolecularSequenceVariant

from fhir_kindling.generators import FhirResourceGenerator
from fhir_kindling import upload_bundle

from dotenv import load_dotenv, find_dotenv


class MolecularSequenceGenerator(FhirResourceGenerator):
    def __init__(self, n: int = None, resources: List[DomainResource] = None,
                 sequence_file: Union[str, List[str]] = None):
        super().__init__(n, resource_type=MolecularSequence)
        self.sequence_file = sequence_file
        if self.sequence_file:
            self.sequences = self._load_sequence_file(self.sequence_file)

    def _generate(self):
        molecular_sequences = []
        for sequence_def in self.sequences:
            mol_seq = self._generate_molecular_sequence(sequence_def[1], sequence_def[2:])
            molecular_sequences.append(mol_seq)
        return molecular_sequences

    def _generate_molecular_sequence(self, sequence: str, variant: List[str]):
        molecular_sequence = MolecularSequence(
            **{
                "coordinateSystem": 0,
                "observedSeq": sequence,
                "variant": self._make_variant_resources(variant)

            }
        )
        return molecular_sequence

    def _make_variant_resources(self, variant: List[str]) -> List[MolecularSequenceVariant]:
        variants = []
        for var in variant:
            variant_resource = MolecularSequenceVariant(
                **{
                    "observedAllele": var
                }
            )
            variants.append(variant_resource)
        return variants

    def _load_sequence_file(self, path: str):
        with open(path, "r") as sf:
            sequences = [line.split() for line in sf.readlines()]
        self.n = len(sequences)
        return sequences


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    sequence_file_1 = "../../examples/hiv_sequences/sequences_1.txt"
    ms_generator = MolecularSequenceGenerator(sequence_file=sequence_file_1)
    resources = ms_generator.generate(generate_ids=True)
    # print(resources)
    bundle = ms_generator.make_bundle()
    print()
    upload_bundle(bundle=bundle, fhir_api_url=os.getenv("FHIR_API_URL"), username=os.getenv("FHIR_USER"),
                  password=os.getenv("FHIR_PW"))
