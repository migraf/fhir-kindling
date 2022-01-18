import pytest
from pydantic import ValidationError

from fhir_kindling.generators.resource_generator import ResourceGenerator, GeneratorParameters, FieldValue
from fhir.resources.condition import Condition
from fhir.resources.patient import Patient
from fhir.resources.organization import Organization
from fhir.resources.observation import Observation
from fhir.resources.fhirtypes import ObservationType
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir_kindling.generators.patient import PatientGenerator
from fhir_kindling.generators.field_generator import FieldGenerator
from fhir_kindling.generators.dataset import DatasetGenerator
from pprint import pp
import datetime


@pytest.fixture
def covid_code():
    covid_code = CodeableConcept(
        coding=[
            Coding(
                system="https://icd.who.int/ct11",
                code="RA01.0",
                display="COVID-19, virus identified"
            )
        ],
        text="COVID-19"
    )
    return covid_code


@pytest.fixture
def covid_params(covid_code):
    # generate patients with ids and turn into an iterator to call as a reference
    patients = PatientGenerator(n=100, generate_ids=True).generate(display=False)
    patient_ids = iter([patient.id for patient in patients])
    params = GeneratorParameters(
        count=100,
        field_values=[
            FieldValue(field="code", value=covid_code),
        ],
        field_generators=[
            FieldGenerator(
                field="subject",
                generator_function=lambda: {"reference": f"Patient/{next(patient_ids)}"}
            )
        ]
    )

    return params, patients, patient_ids


def test_patient_generator():
    patient_generator = PatientGenerator(n=100)
    patients = patient_generator.generate()
    assert len(patients) == 100
    assert isinstance(patients[0], Patient)

    generator = PatientGenerator(n=10, age_range=(18, 60))
    patients = generator.generate()

    with pytest.raises(ValueError):
        generator = PatientGenerator(n=10, age_range=("hello", "world"))
        generator.generate()

    assert len(patients) == 10

    organization_reference = Reference(
        reference="Organization/1",
    )

    generator = PatientGenerator(n=10, age_range=(18, 60), organisation=organization_reference)

    patients = generator.generate()
    assert len(patients) == 10


def test_generator_init():
    with pytest.raises(ValueError):
        generator = ResourceGenerator("Condition", 10)
        generator.generate()

    with pytest.raises(ValueError):
        generator = ResourceGenerator("Condition", n=10, field_values={"hello": "Patient/1"})
        generator.generate()

    with pytest.raises(KeyError):
        generator = ResourceGenerator("jsdkasdh", 10)

    # generator = generator.generate()
    generator = ResourceGenerator("Condition", n=10, field_values={"subject": "Patient/1"})
    assert generator


def test_check_required_fields():
    generator = ResourceGenerator("Condition", n=10, field_values={"subject": "Patient/1"})
    generator = ResourceGenerator("Condition", n=10, field_values={"subject": "Patient/1"})
    generator.required_fields()


def test_generator_field_parameters():
    params = FieldGenerator(field="birthdate", choices=["2018-01-01", "2018-01-02"],
                            choice_probabilities=[0.5, 0.5])
    with pytest.raises(ValidationError):
        params = FieldGenerator(field="birthdate", choices=["2018-01-01", "2018-01-02"],
                                choice_probabilities=[0.5, 0.3, 0.2])

    with pytest.raises(ValidationError):
        params = FieldGenerator(field="birthdate", choices=["2018-01-01", "2018-01-02"],
                                choice_probabilities=[0.5, 0.6])

    with pytest.raises(ValidationError):
        params = FieldGenerator(field="birthdate", choices=["2018-01-01", "2018-01-02"],
                                choice_probabilities=[0.5, 0.5], generator_function=lambda x: "2018-01-01")

    with pytest.raises(ValidationError):
        params = FieldGenerator(field="birthdate")


def test_field_generator():
    choices = ["2018-01-01", "2018-01-02"]
    params = FieldGenerator(field="birthdate", choices=choices, choice_probabilities=[0.5, 0.5])
    value = params.generate()
    assert value in choices

    params = FieldGenerator(field="birthdate", choices=choices)
    value = params.generate()
    assert value in choices

    params = FieldGenerator(field="birthdate", choices=choices, choice_probabilities=[1.0, 0.0])
    for i in range(100):
        value = params.generate()
        assert value == choices[0]

    params = FieldGenerator(field="birthdate", generator_function=lambda: "2018-01-01")
    value = params.generate()
    assert value == "2018-01-01"


def test_generator_with_parameters(covid_params):
    # generate patients with ids and turn into an iterator to call as a reference

    params, patients, patient_ids = covid_params

    generator = ResourceGenerator("Condition", generator_parameters=params)

    resources = generator.generate()

    assert len(resources) == 100


def test_resource_generate_covid_dataset(covid_params):
    # generate patients with ids and turn into an iterator to call as a reference
    params, patients, patient_ids = covid_params

    generator = ResourceGenerator("Condition", generator_parameters=params)


def test_generate_dataset():
    generator = DatasetGenerator("Patient", n=100)

    result = generator.generate()

    assert result.base_resource == "Patient"
    assert len(result.resources[0].resources) == 100
