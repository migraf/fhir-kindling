import os

import orjson
import requests
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.condition import Condition
from fhir.resources.patient import Patient
from fhir.resources.reference import Reference

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

    upload_bundle = Bundle.construct()
    upload_bundle.type = "transaction"
    upload_bundle.entry = []
    print(f"generating upload bundle for patients")
    for i, patient in enumerate(patients):

        request = BundleEntryRequest(
            method="POST",
            url="/Patient"
        )

        entry = BundleEntry(
            request=request,
            resource=patient
        )
        upload_bundle.entry.append(entry)
    upload_bundle = upload_bundle.validate(upload_bundle)
    json_dict = orjson.loads(upload_bundle.json(exclude_none=True))
    print(f"uploading server 1 ({server_1.api_address})...")
    r = requests.post(server_1.api_address, json=json_dict)

    print(f"uploading conditions...")
    condition_entries = []
    for entry in r.json()["entry"]:
        print(f"entry: {entry}")
        reference = "/".join(entry["response"]["location"].split("/")[-4:-2])
        print(f"reference: {reference}")
        covid_condition = Condition(
            code=COVID_CODE,
            subject=Reference(reference=reference)
        )
        request = BundleEntryRequest(
            method="POST",
            url="/Condition"
        )

        entry = BundleEntry(
            request=request,
            resource=covid_condition
        )
        condition_entries.append(entry)

    upload_bundle.entry = condition_entries
    upload_bundle = upload_bundle.validate(upload_bundle)
    json_dict = orjson.loads(upload_bundle.json(exclude_none=True))
    print(f"uploading conditions server 1 ({server_1.api_address})...")
    r = requests.post(server_1.api_address, json=json_dict)

    r.raise_for_status()
    # print(r.headers)
    # print(f"uploading server 2 ({server_2.api_address})...")
    # r = requests.post(server_2.api_address, json=json_dict)
    # print(r.text)
    # print(r.headers)
    # r.raise_for_status()


COVID_CODE = CodeableConcept(
    coding=[
        Coding(
            system="http://id.who.int/icd/release/11/mms",
            code="RA01.0",
            display="COVID-19, virus identified"
        )
    ],
    text="COVID-19"
)

if __name__ == '__main__':
    prefill()
