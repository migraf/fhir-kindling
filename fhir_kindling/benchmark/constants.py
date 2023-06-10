from enum import Enum


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
