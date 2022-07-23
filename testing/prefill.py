import os

import orjson
import requests
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir_kindling import FhirServer
from fhir_kindling.generators import DatasetGenerator, GeneratorParameters, FieldValue, ResourceGenerator, \
    PatientGenerator, FieldGenerator


def prefill():
    server_1 = os.getenv("FHIR_API_URL", "http://localhost:9090/fhir")
    server_2 = os.getenv("TRANSFER_API_URL", "http://localhost:9091/fhir")

    assert server_1
    assert server_2

    server_1 = FhirServer(api_address=server_1)
    server_2 = FhirServer(api_address=server_2)

    print(f"initialized server_1: {server_1}")
    print(f"initialized server_2: {server_2}")

    count = 20
    patients = PatientGenerator(n=count).generate()
    print(f"generated {len(patients)} patients")

    patient_entries = []
    upload_bundle = Bundle.construct()
    upload_bundle.type = "transaction"
    upload_bundle.entry = []
    for patient in patients:
        entry = BundleEntry().construct()
        entry.request = BundleEntryRequest(
            **{
                "method": "POST",
                "url": patient.get_resource_type()
            }
        )
        entry.resource = patient

        patient_entries.extend(entry)

    json_dict = orjson.loads(upload_bundle.json(exclude_none=True))
    print("uploading server 1...")
    r = requests.post(server_1.api_address, json=json_dict)
    r.raise_for_status()
    print("uploading server 2...")
    r = requests.post(server_2.api_address, json=json_dict)
    r.raise_for_status()


if __name__ == '__main__':
    prefill()
