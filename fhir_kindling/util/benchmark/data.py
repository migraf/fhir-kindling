from enum import Enum

import pendulum
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding

from fhir_kindling.generators.dataset import DatasetGenerator
from fhir_kindling.generators.field_generator import FieldGenerator
from fhir_kindling.generators.resource_generator import (
    FieldValue,
    GeneratorParameters,
    ResourceGenerator,
)

N_BASE_RESOURCES = 5000


def generate_benchmark_data(n_patients: int = N_BASE_RESOURCES):
    dataset = DatasetGenerator("Patient", n=n_patients)
    covid_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=Codes.COVID.value),
        ]
    )
    covid_generator = ResourceGenerator("Condition", generator_parameters=covid_params)
    dataset.add_resource(covid_generator, name="covid")
    vaccination_date_generator = FieldGenerator(
        field="occurrenceDateTime",
        generator_function=lambda: pendulum.now().to_date_string(),
    )

    first_vax_params = GeneratorParameters(
        field_values=[
            FieldValue(field="vaccineCode", value=Codes.COVID_VACC_RNA.value),
            FieldValue(field="status", value="completed"),
        ],
        field_generators=[vaccination_date_generator],
    )
    vaccination_generator = ResourceGenerator(
        "Immunization", generator_parameters=first_vax_params
    )

    dataset.add_resource(vaccination_generator, "first shot mrna")

    result = dataset.generate(ids=True)
    print(result)


class Codes(Enum):
    COVID = CodeableConcept(
        coding=[
            Coding(
                system="http://id.who.int/icd/release/11/mms",
                code="RA01.0",
                display="COVID-19, virus identified",
            )
        ],
        text="COVID-19",
    )
    COVID_VACC_RNA = CodeableConcept(
        coding=[
            Coding(
                system="http://id.who.int/icd/release/11/mms",
                code="XM0GQ8",
                display="COVID-19 vaccine, RNA based",
            )
        ],
        text="COVID vaccination",
    )
