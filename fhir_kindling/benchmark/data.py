import random
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

N_BASE_RESOURCES = 100


def generate_benchmark_data(n_patients: int = N_BASE_RESOURCES) -> DatasetGenerator:
    dataset = DatasetGenerator("Patient", n=n_patients)

    # covid
    covid_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=Codes.COVID.value),
        ]
    )
    covid_generator = ResourceGenerator("Condition", generator_parameters=covid_params)
    dataset.add_resource_generator(covid_generator, name="covid")

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
        "Immunization", generator_parameters=first_vax_params
    )

    dataset.add_resource_generator(vaccination_generator, "vacc-mrna-1", likelihood=0.7)

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

    dataset.add_resource_generator(
        second_vaccination_generator,
        "vacc-mrna-2",
        depends_on="vacc-mrna-1",
        likelihood=0.9,
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

    dataset.add_resource_generator(
        third_vaccination_generator,
        "vacc-mrna-3",
        depends_on=["vacc-mrna-1", "vacc-mrna-2"],
        likelihood=0.7,
    )

    emergency_encounter_period_generator = FieldGenerator(
        field="period",
        generator_function=lambda: {
            "start": pendulum.now().subtract(days=730).to_date_string(),
            "end": pendulum.now().subtract(days=729).to_date_string(),
        },
    )
    # generate encounters

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

    dataset.add_resource_generator(
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
            FieldValue(field="type", value=Codes.ICU_ENCOUNTER.value),
            FieldValue(field="status", value="finished"),
        ],
        field_generators=[icu_encounter_period_generator],
    )

    icu_encounter_generator = ResourceGenerator(
        "Encounter", generator_parameters=icu_encounter_params
    )

    dataset.add_resource_generator(
        icu_encounter_generator,
        "icu-encounter",
        depends_on=["base", "emergency-encounter"],
        reference_field="subject",
    )

    # generate observations

    # blood oxygen saturation
    blood_oxygen_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=Codes.OXYGEN_SATURATION.value),
            FieldValue(field="status", value="final"),
            FieldValue(field="unit", value="%"),
        ],
        field_generators=[
            FieldGenerator(
                field="value",
                generator_function=lambda: random.randint(90, 100),
            ),
        ],
    )
    blood_oxygen_saturation_generator = ResourceGenerator(
        "Observation", generator_parameters=blood_oxygen_params
    )

    dataset.add_resource_generator(
        blood_oxygen_saturation_generator,
        "blood-oxygen-saturation",
        depends_on="icu-encounter",
    )

    # body temperature
    body_temperature_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=Codes.BODY_TEMPERATURE.value),
            FieldValue(field="status", value="final"),
            FieldValue(field="unit", value="°C"),
        ],
        field_generators=[
            FieldGenerator(
                field="value",
                generator_function=lambda: random.randint(36, 40) + random.random(),
            ),
        ],
    )

    body_temperature_generator = ResourceGenerator(
        "Observation", generator_parameters=body_temperature_params
    )

    dataset.add_resource_generator(
        body_temperature_generator,
        "body-temperature",
        depends_on="icu-encounter",
    )

    # respiratory rate
    respiratory_rate_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=Codes.RESPIRATORY_RATE.value),
            FieldValue(field="status", value="final"),
            FieldValue(field="unit", value="breaths/min"),
        ],
        field_generators=[
            FieldGenerator(
                field="value",
                generator_function=lambda: random.randint(12, 20),
            ),
        ],
    )

    respiratory_rate_generator = ResourceGenerator(
        "Observation", generator_parameters=respiratory_rate_params
    )

    dataset.add_resource_generator(
        respiratory_rate_generator,
        "respiratory-rate",
        depends_on="icu-encounter",
    )

    # heart rate
    heart_rate_params = GeneratorParameters(
        field_values=[
            FieldValue(field="code", value=Codes.HEART_RATE.value),
            FieldValue(field="status", value="final"),
            FieldValue(field="unit", value="beats/min"),
        ],
        field_generators=[
            FieldGenerator(
                field="value",
                generator_function=lambda: random.randint(60, 100),
            ),
        ],
    )

    heart_rate_generator = ResourceGenerator(
        "Observation", generator_parameters=heart_rate_params
    )

    dataset.add_resource_generator(
        heart_rate_generator,
        name="heart-rate",
        depends_on="icu-encounter",
    )

    return dataset


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
    EMERGENCY_ENCOUNTER = CodeableConcept(
        coding=[
            Coding(
                system="http://terminology.hl7.org/ValueSet/v3-ActEncounterCode",
                code="EMER",
                display="emergency",
            )
        ],
        text="Emergency",
    )
    ICU_ENCOUNTER = CodeableConcept(
        coding=[
            Coding(
                system="http://terminology.hl7.org/ValueSet/v3-ActEncounterCode",
                code="IMP",
                display="inpatient encounter",
            )
        ],
        text="Inpatient",
    )
    ICU_ENCOUNTER_TYPE = CodeableConcept(
        coding=[
            Coding(
                system="http://loinc.org",
                code="99222",
                display="Inpatient Hospitalization",
            )
        ],
    )

    OXYGEN_SATURATION = CodeableConcept(
        coding=[
            Coding(
                system="http://loinc.org",
                code="55284-4",
                display="Oxygen saturation in Arterial blood by Pulse oximetry",
            )
        ],
    )

    BODY_TEMPERATURE = CodeableConcept(
        coding=[
            Coding(
                system="http://loinc.org",
                code="99836-5",
                display="Body temperature",
            )
        ]
    )

    RESPIRATORY_RATE = CodeableConcept(
        coding=[
            Coding(
                system="http://loinc.org",
                code="9279-1",
                display="Respiratory rate",
            )
        ]
    )

    HEART_RATE = CodeableConcept(
        coding=[
            Coding(
                system="http://loinc.org",
                code="8802-8",
                display="Heart rate",
            )
        ],
    )
