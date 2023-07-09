import os
import time

import httpx
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding

from fhir_kindling import FhirServer
from fhir_kindling.generators.dataset import DatasetGenerator
from fhir_kindling.generators.resource_generator import (
    FieldValue,
    GeneratorParameters,
    ResourceGenerator,
)


def check_server_status(
    server_1: str,
    server_2: str,
):
    increments = [5, 10, 30, 30, 60, 120]
    for increment in increments:
        try:
            print(f"checking server 1 ({server_1})...")
            r = httpx.get(server_1 + "/Patient?")
            print(r.text)
            print(r.headers)
            r.raise_for_status()
            server_1_status = True
        except Exception as e:
            print("Server 1 is down")
            print(e)
            server_1_status = False

        try:
            print(f"checking server 2 ({server_2})...")
            r = httpx.get(server_2 + "/Patient?")
            print(r.text)
            print(r.headers)
            r.raise_for_status()
            server_2_status = True
        except Exception as e:
            print("Server 2 is down")
            print(e)
            server_2_status = False

        if server_1_status and server_2_status:
            return True
        else:
            print(f"waiting {increment} seconds...")
            time.sleep(increment)

    return False


def prefill():
    server_1 = os.getenv("FHIR_API_URL", "http://localhost:9090/fhir")
    server_2 = os.getenv("TRANSFER_SERVER_URL", "http://localhost:9091/fhir")

    if not check_server_status(server_1, server_2):
        print("Servers are down. Exiting...")
        raise Exception("Servers are down. Exiting...")

    assert server_1
    assert server_2

    server_1 = FhirServer(api_address=server_1)
    server_2 = FhirServer(api_address=server_2)

    print(f"initialized server_1: {server_1}")
    print(f"initialized server_2: {server_2}")

    time.sleep(5)

    count = 20
    # create dataset generator

    dataset_generator = DatasetGenerator(n=count, name="prefill")

    # add covid condition
    COVID_CODE = CodeableConcept(
        coding=[
            Coding(
                system="http://id.who.int/icd/release/11/mms",
                code="RA01.0",
                display="COVID-19, virus identified",
            )
        ],
        text="COVID-19",
    )

    covid_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=COVID_CODE),
        ]
    )
    covid_generator = ResourceGenerator("Condition", generator_parameters=covid_params)
    dataset_generator.add_resource_generator(
        covid_generator, name="covid", depends_on="base", reference_field="subject"
    )

    dataset_1 = dataset_generator.generate()

    print(f"generated dataset: {dataset_1}")

    # upload dataset to server 1
    print(f"uploading dataset to server 1 ({server_1.api_address})...")
    dataset_1.upload(server_1)

    # upload to server 2
    dataset_2 = dataset_generator.generate()

    print(f"generated dataset: {dataset_2}")

    # upload dataset to server 1
    print(f"uploading dataset to server 1 ({server_1.api_address})...")
    dataset_2.upload(server_1)


if __name__ == "__main__":
    prefill()
