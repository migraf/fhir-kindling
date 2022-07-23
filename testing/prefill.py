import os

import pendulum
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding

from fhir_kindling import FhirServer
from fhir_kindling.generators import DatasetGenerator, GeneratorParameters, FieldValue, ResourceGenerator, \
    PatientGenerator, FieldGenerator


def prefill():
    server_1 = os.getenv("FHIR_API_URL")
    server_2 = os.getenv("TRANSFER_API_URL")

    server_1 = FhirServer(api_address=server_1)
    server_2 = FhirServer(api_address=server_2)

    count = 20
    dataset_generator = DatasetGenerator("Patient", n=count)

    covid_code = CodeableConcept(
        coding=[
            Coding(
                system="http://id.who.int/icd/release/11/mms",
                code="RA01.0",
                display="COVID-19, virus identified"
            )
        ],
        text="COVID-19"
    )

    vaccination_code = CodeableConcept(
        coding=[
            Coding(
                system="http://id.who.int/icd/release/11/mms",
                code="XM0GQ8",
                display="COVID-19 vaccine, RNA based"
            )
        ],
        text="COVID vaccination"
    )

    covid_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=covid_code),
        ]
    )

    covid_generator = ResourceGenerator("Condition", generator_parameters=covid_params)
    # add covid conditions to patients
    dataset_generator.add_resource(covid_generator, name="covid")

    patients, patient_ids = PatientGenerator(n=count, generate_ids=True).generate(references=True)

    vaccination_date_generator = FieldGenerator(
        field="occurrenceDateTime",
        generator_function=lambda: pendulum.now().to_date_string()
    )

    first_vax_params = GeneratorParameters(
        field_values=[
            FieldValue(field="vaccineCode", value=vaccination_code),
            FieldValue(field="status", value="completed"),
        ],
        field_generators=[
            vaccination_date_generator
        ]
    )
    vaccination_generator = ResourceGenerator("Immunization", generator_parameters=first_vax_params)
    dataset_generator.add_resource(vaccination_generator, name="first_vaccination", likelihood=0.8)

    dataset = dataset_generator.generate(ids=True)
    # pprint(result.dict(exclude_none=True))

    dataset.upload(server_1)
    dataset.upload(server_2)


if __name__ == '__main__':
    prefill()
