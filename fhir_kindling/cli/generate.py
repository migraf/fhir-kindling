import os
from pathlib import Path
from typing import List, Union

from fhir.resources.bundle import Bundle
from fhir.resources.organization import Organization
from fhir.resources.reference import Reference
from fhir.resources.identifier import Identifier

from fhir_kindling.generators import FhirResourceGenerator, PatientResourceGenerator, MolecularSequenceGenerator, \
    PatientGenerator
from .upload import upload_bundle, upload_resource
from dotenv import load_dotenv, find_dotenv


# TODO clean up authentication flow

def generate_data_set(name: str, generators: List[FhirResourceGenerator] = None, bundle: Union[Bundle, str] = None,
                      fhir_api_url: str = None,
                      username: str = None,
                      password: str = None,
                      token: str = None,
                      fhir_server_type: str = "hapi",
                      out_dir: Union[str, Path] = None, filename: str = None):
    if not (generators or bundle):
        raise ValueError("Either bundle or generators need to be given to generate a data set.")

    # create organisation to group generated patients under
    organisation = create_organisation_for_data_set(name)

    # register it with the server and get the reference
    r, organisation_reference = upload_resource(organisation,
                                                fhir_api_url=fhir_api_url,
                                                username=username,
                                                password=password,
                                                token=token,
                                                fhir_server_type=fhir_server_type,
                                                reference=True
                                                )

    if generators:
        exit_code = _make_data_set_with_generators(generators=generators, organisation_reference=organisation_reference,
                                                   fhir_api_url=fhir_api_url, username=username, password=password,
                                                   token=token, fhir_server_type=fhir_server_type)

        return exit_code

    elif bundle:
        # TODO upload bundle as data set
        pass

    return 0


def _make_data_set_with_generators(generators: List[FhirResourceGenerator],
                                   organisation_reference: Reference,
                                   fhir_api_url: str = None,
                                   username: str = None,
                                   password: str = None,
                                   token: str = None,
                                   fhir_server_type: str = "hapi"
                                   ):
    num_patients = max([gen.num_patients for gen in generators])
    print(f"Generating {num_patients} Patients for the defined resources.")
    # Generate patients and upload bundle to get server assigned ids
    patient_generator = PatientGenerator(n=num_patients, organisation=organisation_reference)
    patients = patient_generator.generate()
    response, patient_references = upload_bundle(bundle=patient_generator.make_bundle(), fhir_api_url=fhir_api_url,
                                                 username=username, password=password, token=token,
                                                 fhir_server_type=fhir_server_type,
                                                 references=True)

    for gen in generators:
        resources = gen.generate(patient_references=patient_references)
        response = upload_bundle(gen.make_bundle(), fhir_api_url=fhir_api_url, username=username, password=password,
                                 token=token, fhir_server_type=fhir_server_type)

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
    sequence_file_5 = "../../examples/hiv_sequences/sequences_5.txt"
    sequence_file_4 = "../../examples/hiv_sequences/sequences_4.txt"
    sequence_file_3 = "../../examples/hiv_sequences/sequences_3.txt"
    ms_generator = MolecularSequenceGenerator(sequence_file=[sequence_file_3, sequence_file_4])

    dataset = generate_data_set(name="HIV_DEMO", generators=[ms_generator],
                                fhir_api_url="https://ibm-fhir.personalhealthtrain.de/fhir-server/api/v4",
                                fhir_server_type="ibm")
