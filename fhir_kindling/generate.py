import os
from pathlib import Path
from typing import List, Union
from fhir.resources.organization import Organization

from fhir_kindling.generators import FhirResourceGenerator, PatientResourceGenerator, MolecularSequenceGenerator, \
    PatientGenerator
from fhir_kindling.upload import upload_bundle, upload_resource
from dotenv import load_dotenv, find_dotenv

# TODO clean up authentication flow

def generate_data_set(name: str, generators: List[FhirResourceGenerator], fhir_api_url: str = None,
                      out_dir: Union[str, Path] = None, filename: str = None):
    # create organisation to group generated patients under
    organisation = create_organisation_for_data_set(name)
    # register it with the server and get the reference
    r, organisation_reference = upload_resource(organisation,
                                   fhir_api_url=fhir_api_url if fhir_api_url else os.getenv("FHIR_API_URL"))

    num_patients = max([gen.num_patients for gen in generators])
    print(f"Generating {num_patients} for the defined resources.")

    # Generate patients and upload bundle to get server assigned ids
    patient_generator = PatientGenerator(n=num_patients, organisation=organisation_reference)
    patients = patient_generator.generate()
    response, patient_references = upload_bundle(bundle=patient_generator.make_bundle(), fhir_api_url=fhir_api_url, references=True)
    print(patient_references)
    for gen in generators:
        resources = gen.generate(patient_references=patient_references)
        response = upload_bundle(gen.make_bundle(), fhir_api_url=fhir_api_url)
        print(response)

    return 0


def generate_resources(generator: Union[FhirResourceGenerator, PatientResourceGenerator],
                       patient_references: List[str] = None, fhir_api_url: str = None,
                       out_dir: Union[str, Path] = None, filename: str = None):
    if isinstance(generator, FhirResourceGenerator):
        resources = generator.generate(out_dir=out_dir, filename=filename)
        return resources, generator.make_bundle()
    # Generate patients for resources and initially register
    elif isinstance(generator, PatientResourceGenerator):
        if not patient_references:
            patients_bundle = generator.generate_patients(bundle=True)
            response, patient_references = upload_bundle(patients_bundle, references=True, fhir_api_url=fhir_api_url)

        resources, bundle = generator.generate(patient_references, out_dir, filename)
        return resources, bundle


def create_organisation_for_data_set(name: str) -> Organization:
    org = Organization(
        **{
            "active": True,
            "name": name
        }
    )
    return org


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    # sequence_file = "../examples/hiv_sequences/sequences_2.txt"
    # mol_seq_generator = MolecularSequenceGenerator(sequence_file=sequence_file)
    # patient_ms_generator = PatientResourceGenerator(resource_generator=mol_seq_generator)
    # resources, bundle = generate_resources(patient_ms_generator, fhir_api_url=os.getenv("FHIR_API_URL"), out_dir=".",
    #                                        filename="sequence_bundle.json")
    #
    # upload_bundle(bundle=bundle, fhir_api_url=os.getenv("FHIR_API_URL"))
    sequence_file_1 = "../examples/hiv_sequences/sequences_2.txt"
    sequence_file_2 = "../examples/hiv_sequences/sequences_4.txt"
    ms_generator = MolecularSequenceGenerator(sequence_file=[sequence_file_1, sequence_file_2])

    dataset = generate_data_set(name="DEMO_HIV", generators=[ms_generator],
                                fhir_api_url=os.getenv("FHIR_API_URL"))
