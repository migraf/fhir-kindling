import random

import pendulum

from fhir_kindling.benchmark.constants import Codes
from fhir_kindling.generators.dataset import DatasetGenerator
from fhir_kindling.generators.field_generator import FieldGenerator
from fhir_kindling.generators.resource_generator import (
    FieldValue,
    GeneratorParameters,
    ResourceGenerator,
)
from fhir_kindling.generators.time_series_generator import TimeSeriesGenerator

N_BASE_RESOURCES = 100


def generate_benchmark_data(n_patients: int = N_BASE_RESOURCES) -> DatasetGenerator:
    dataset_generator = DatasetGenerator("Patient", n=n_patients)

    # covid
    covid_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=Codes.COVID.value),
        ]
    )
    covid_generator = ResourceGenerator("Condition", generator_parameters=covid_params)
    dataset_generator.add_resource_generator(
        covid_generator, name="covid", depends_on="base", reference_field="subject"
    )

    # covid vaccination(s)

    vaccination_date_generator = FieldGenerator(
        field="occurrenceDateTime",
        generator_function=lambda: pendulum.now().to_date_string(),
    )

    # first shot covid vaccine

    first_vax_params = GeneratorParameters(
        field_values=[
            FieldValue(field="vaccineCode", value=Codes.COVID_VACC_RNA.value),
            FieldValue(field="status", value="completed"),
        ],
        field_generators=[vaccination_date_generator],
    )
    vaccination_generator = ResourceGenerator(
        "Immunization",
        generator_parameters=first_vax_params,
    )

    dataset_generator.add_resource_generator(
        vaccination_generator,
        "vacc-mrna-1",
        depends_on="base",
        likelihood=0.7,
        reference_field="patient",
    )

    # second shot
    second_vax_params = GeneratorParameters(
        field_values=[
            FieldValue(field="vaccineCode", value=Codes.COVID_VACC_RNA.value),
            FieldValue(field="status", value="completed"),
        ],
        field_generators=[vaccination_date_generator],
    )
    second_vaccination_generator = ResourceGenerator(
        "Immunization", generator_parameters=second_vax_params
    )

    dataset_generator.add_resource_generator(
        second_vaccination_generator,
        "vacc-mrna-2",
        depends_on=["base", "vacc-mrna-1"],
        likelihood=0.9,
        reference_field=["patient", None],
    )

    # third shot
    second_vax_params = GeneratorParameters(
        field_values=[
            FieldValue(field="vaccineCode", value=Codes.COVID_VACC_RNA.value),
            FieldValue(field="status", value="completed"),
        ],
        field_generators=[vaccination_date_generator],
    )
    third_vaccination_generator = ResourceGenerator(
        "Immunization", generator_parameters=second_vax_params
    )

    dataset_generator.add_resource_generator(
        third_vaccination_generator,
        "vacc-mrna-3",
        depends_on=["base", "vacc-mrna-1", "vacc-mrna-2"],
        reference_field=["patient", None, None],
        likelihood=0.7,
    )
    # generate encounters
    emergency_encounter_period_generator = FieldGenerator(
        field="period",
        generator_function=lambda: {
            "start": pendulum.now().subtract(days=730).to_date_string(),
            "end": pendulum.now().subtract(days=729).to_date_string(),
        },
    )

    # emergency encounter
    emergency_encounter_params = GeneratorParameters(
        field_values=[
            FieldValue(field="class", value=Codes.EMERGENCY_ENCOUNTER.value),
            FieldValue(field="status", value="finished"),
        ],
        field_generators=[emergency_encounter_period_generator],
    )

    emergency_encounter_generator = ResourceGenerator(
        "Encounter", generator_parameters=emergency_encounter_params
    )

    dataset_generator.add_resource_generator(
        emergency_encounter_generator,
        "emergency-encounter",
        depends_on="base",
        reference_field="subject",
    )

    icu_encounter_period_generator = FieldGenerator(
        field="period",
        generator_function=lambda: {
            "start": pendulum.now().subtract(days=720).to_date_string(),
            "end": pendulum.now().subtract(days=710).to_date_string(),
        },
    )

    # icu encounter
    icu_encounter_params = GeneratorParameters(
        field_values=[
            FieldValue(field="class", value=Codes.ICU_ENCOUNTER.value),
            FieldValue(
                field="type", value=Codes.ICU_ENCOUNTER_TYPE.value, list_field=True
            ),
            FieldValue(field="status", value="finished"),
        ],
        field_generators=[icu_encounter_period_generator],
    )

    icu_encounter_generator = ResourceGenerator(
        "Encounter", generator_parameters=icu_encounter_params
    )

    dataset_generator.add_resource_generator(
        icu_encounter_generator,
        "icu-encounter",
        depends_on=["base", "emergency-encounter"],
        reference_field=["subject", None],
    )

    # generate observations

    # blood oxygen saturation
    blood_oxygen_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=Codes.OXYGEN_SATURATION.value),
            FieldValue(field="status", value="final"),
        ],
        field_generators=[
            FieldGenerator(
                field="valueQuantity",
                generator_function=lambda: {
                    "value": random.randint(90, 100),
                    "unit": "%",
                },
            ),
        ],
    )
    blood_oxygen_saturation_generator = ResourceGenerator(
        "Observation", generator_parameters=blood_oxygen_params
    )

    bo_time_series_generator = TimeSeriesGenerator(
        resource_generator=blood_oxygen_saturation_generator,
        start=pendulum.now().subtract(days=720),
        n=10,
        time_field="effectiveDateTime",
        freq="daily",
    )

    dataset_generator.add_resource_generator(
        bo_time_series_generator,
        "blood-oxygen-saturation",
        depends_on="base",
        reference_field="subject",
    )

    # body temperature
    body_temperature_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=Codes.BODY_TEMPERATURE.value),
            FieldValue(field="status", value="final"),
        ],
        field_generators=[
            FieldGenerator(
                field="valueQuantity",
                generator_function=lambda: {
                    "value": random.randint(36, 40) + random.random(),
                    "unit": "°C",
                },
            ),
        ],
    )

    body_temperature_generator = ResourceGenerator(
        "Observation", generator_parameters=body_temperature_params
    )

    dataset_generator.add_resource_generator(
        body_temperature_generator,
        "body-temperature",
        depends_on="icu-encounter",
        reference_field="encounter",
    )

    # respiratory rate
    respiratory_rate_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=Codes.RESPIRATORY_RATE.value),
            FieldValue(field="status", value="final"),
        ],
        field_generators=[
            FieldGenerator(
                field="valueQuantity",
                generator_function=lambda: {
                    "value": random.randint(12, 30),
                    "unit": "breaths/min",
                },
            ),
        ],
    )

    respiratory_rate_generator = ResourceGenerator(
        "Observation", generator_parameters=respiratory_rate_params
    )

    dataset_generator.add_resource_generator(
        respiratory_rate_generator,
        "respiratory-rate",
        depends_on="icu-encounter",
        reference_field="encounter",
    )

    # heart rate
    heart_rate_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=Codes.HEART_RATE.value),
            FieldValue(field="status", value="final"),
        ],
        field_generators=[
            FieldGenerator(
                field="valueQuantity",
                generator_function=lambda: {
                    "value": random.randint(60, 100),
                    "unit": "beats/min",
                },
            ),
        ],
    )

    heart_rate_generator = ResourceGenerator(
        "Observation", generator_parameters=heart_rate_params
    )

    dataset_generator.add_resource_generator(
        heart_rate_generator,
        name="heart-rate",
        depends_on="icu-encounter",
        reference_field="encounter",
    )

    return dataset_generator
