from pathlib import Path
from typing import List, Union

from fhir_kindling.generators import FhirResourceGenerator, PatientResourceGenerator, MolecularSequenceGenerator
from fhir_kindling.upload import upload_bundle


def generate_data_set(name: str, generators: List[Union[FhirResourceGenerator, PatientResourceGenerator]]):
    pass


def generate_resources(generator: Union[FhirResourceGenerator, PatientResourceGenerator],
                      out_dir: Union[str, Path] = None, filename: str = None):
    if isinstance(generator, FhirResourceGenerator):
        resources = generator.generate(out_dir=out_dir, filename=filename)

    elif isinstance(generator, PatientResourceGenerator):
        patients_bundle = generator.generate_patients(bundle=True)
        patient_ids = upload_bundle(patients_bundle, ids=True)



if __name__ == '__main__':
    sequence_file = "../examples/hiv_sequences/sequences_2.txt"
    mol_seq_generator = MolecularSequenceGenerator(sequence_file=sequence_file)
    patient_ms_generator = PatientResourceGenerator(resource_generator=mol_seq_generator)
    generate_resources(patient_ms_generator)
