import pytest
from fhir_kindling.generators.resource_generator import ResourceGenerator
from fhir.resources.condition import Condition
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.fhirtypes import ObservationType
from fhir_kindling.generators.patient import PatientGenerator
from pprint import pp


def test_patient_generator_init():
    patient_generator = PatientGenerator(n=100)
    patients = patient_generator.generate()
    assert len(patients) == 100


def test_generator_init():
    generator = ResourceGenerator("Condition", 10)
    assert isinstance(generator.resource, Condition)
    with pytest.raises(KeyError):
        generator = ResourceGenerator("jsdkasdh", 10)

    patient_generator = ResourceGenerator("Patient", 10)

    patient_generator.required_fields()


def test_check_required_fields():
    generator = ResourceGenerator("Condition", 10)
    with pytest.raises(ValueError):
        generator.generate()

    generator = ResourceGenerator("Condition", n=10, field_values={"hello": "Patient/1"})
    with pytest.raises(ValueError):
        generator.generate()

    generator = ResourceGenerator("Condition", n=10, field_values={"subject": "Patient/1"})
    generator.generate()

def test_resource_generation():
    generator = ResourceGenerator("Condition", n=10, field_values={"subject": "Patient/1"})