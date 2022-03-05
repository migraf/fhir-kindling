import os

import pytest
from dotenv import load_dotenv, find_dotenv
from pydantic import ValidationError

from fhir_kindling import FhirServer
from fhir_kindling.generators.resource_generator import ResourceGenerator, GeneratorParameters, FieldValue
from fhir.resources.condition import Condition
from fhir.resources.patient import Patient
from fhir.resources.organization import Organization
from fhir.resources.observation import Observation
from fhir.resources.fhirtypes import ObservationType
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.immunization import Immunization
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir_kindling.generators.patient import PatientGenerator
from fhir_kindling.generators.field_generator import FieldGenerator
from fhir_kindling.generators.dataset import DatasetGenerator
from pprint import pp, pprint
import datetime
import pendulum


@pytest.fixture
def api_url():
    """
    Base api url and env vars
    """
    load_dotenv(find_dotenv())

    return os.getenv("FHIR_API_URL", "http://test.fhir.org/r4")


@pytest.fixture
def server(api_url):
    server = FhirServer(
        api_address=api_url,
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL")
    )
    return server


@pytest.fixture
def covid_code():
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
    return covid_code


@pytest.fixture
def vaccination_code():
    covid_code = CodeableConcept(
        coding=[
            Coding(
                system="http://id.who.int/icd/release/11/mms",
                code="XM0GQ8",
                display="COVID-19 vaccine, RNA based"
            )
        ],
        text="COVID vaccination"
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

    print(generator)
    patients = generator.generate()
    assert len(patients) == 10


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
    params, patients, patient_ids = covid_params

    generator = ResourceGenerator("Condition", generator_parameters=params)

    resources = generator.generate()

    assert len(resources) == 100


def test_resource_generator(covid_code):
    patient_generator = PatientGenerator(n=100, generate_ids=True)
    patients, references = patient_generator.generate(references=True)

    references_iter = iter(references)

    params = GeneratorParameters(
        count=100,
        field_values=[

        ],
        field_generators=[
            # user patient reference iterator to generate subject field
            FieldGenerator(field="subject", generator_function=lambda: next(references_iter)),
        ]
    )

    generator = ResourceGenerator("Condition", generator_parameters=params)
    data = generator.generate()

    assert len(data) == 100

    params = GeneratorParameters(
        count=100,
        field_values=[
            FieldValue(field="subject", value=references),
        ],
    )

    generator = ResourceGenerator("Condition", generator_parameters=params)
    data = generator.generate()
    assert len(data) == 100

    # too few resources in field value
    with pytest.raises(ValueError):
        params = GeneratorParameters(
            count=200,
            field_values=[
                FieldValue(field="subject", value=references),
            ],
        )

        generator = ResourceGenerator("Condition", generator_parameters=params)
        data = generator.generate()

    # duplicate field values should raise error
    with pytest.raises(ValueError):
        patient_2, reference_2 = patient_generator.generate(references=True)
        params = GeneratorParameters(
            count=100,
            field_values=[
                FieldValue(field="subject", value=references),
                FieldValue(field="subject", value=reference_2),
            ],
        )

        generator = ResourceGenerator("Condition", generator_parameters=params)
        data = generator.generate()

    references_iter_2 = iter(references)

    # generator and value targeting the same field should raise error
    with pytest.raises(ValueError):
        patient_2, reference_2 = patient_generator.generate(references=True)
        params = GeneratorParameters(
            count=100,
            field_values=[
                FieldValue(field="subject", value=references),
                FieldGenerator(field="subject", generator_function=lambda: next(references_iter_2)),
            ],
        )

        generator = ResourceGenerator("Condition", generator_parameters=params)
        data = generator.generate()


def test_generate_covid_dataset(vaccination_code, covid_code, server):
    count = 100
    dataset_generator = DatasetGenerator("Patient", n=count)

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
    print(vaccination_generator)
    dataset_generator.add_resource(vaccination_generator, name="first_vaccination", likelihood=0.8)

    dataset = dataset_generator.generate(ids=True)
    print(dataset)
    # pprint(result.dict(exclude_none=True))

    dataset.upload(server)
