from enum import Enum

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding


class BenchmarkOperations(str, Enum):
    GENERATE = "generate"
    INSERT = "insert"
    BATCH_INSERT = "batch_insert"
    DATASET_INSERT = "dataset_insert"
    QUERY = "query"
    UPDATE = "update"
    DELETE = "delete"
    BATCH_DELETE = "batch_delete"


class DefaultQueries(str, Enum):
    PATIENTS = "Patient?"
    # Filter patients by birthdate
    PATIENT_BY_BIRTHDATE = "Patient?birthdate=lt2020&birthdate=gt1970"
    # Include observaations
    PATIENTS_WITH_OBSERVATIONS = "Patient?_revinclude=Observation:subject"
    # Patients with emergency encounter with immunization included
    PATIENTS_WITH_EMERGENCY_ENCOUNTER = (
        "Patient?_has:Encounter:subject:class=EMER&_revinclude=Immunization:patient"
    )
    # Immunization for patients with covid code
    IMMUNIZATION_FOR_COVID_PATIENTS = (
        "Patient?_has:Condition:subject:code=RA01.0&_revinclude=Immunization:patient"
    )
    # get observations with am observed breating rate of 20 or less and rev include patients
    PATIENTS_BY_OBSERVATION_VALUE = (
        "Observation?component-code-value-quantity="
        "http://loinc.org|9279-1$lt20&_include=Observation:subject"
    )  # noqa


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
    EMERGENCY_ENCOUNTER = Coding(
        system="http://terminology.hl7.org/ValueSet/v3-ActEncounterCode",
        code="EMER",
        display="emergency",
    )

    ICU_ENCOUNTER = Coding(
        system="http://terminology.hl7.org/ValueSet/v3-ActEncounterCode",
        code="ACUTE",
        display="Acute inpatient encounter",
    )
    ICU_ENCOUNTER_TYPE = [
        CodeableConcept(
            coding=[
                Coding(
                    system="http://loinc.org",
                    code="99222",
                    display="Inpatient Hospitalization",
                )
            ],
        )
    ]

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
