import os

import pytest
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation

from fhir_kindling import FhirServer
from fhir_kindling.util.resources import get_resource_fields
from fhir_kindling.util.references import extract_references, _resource_ids_from_query_response, validate_references
from dotenv import load_dotenv, find_dotenv


@pytest.fixture
def server():
    load_dotenv(find_dotenv())
    server = FhirServer(
        api_address=os.getenv("FHIR_API_URL"),
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL")
    )
    return server

def test_get_resource_fields():
    fields = get_resource_fields(Patient)

    string_fields = get_resource_fields("Patient")

    assert fields == string_fields


def test_extract_references():
    obs_dict = {
        "status": "final",
        "subject": {"reference": "Patient/123"},
        "specimen": {"reference": "Specimen/123"},
        "device": {"reference": "Device/123"},
        "code": {"coding": [{"system": "http://loinc.org", "code": "123"}]},
    }

    obs = Observation(**obs_dict)

    references = extract_references(obs)
    assert len(references) == 3

    assert ("Patient", "123") in references
    assert ("Specimen", "123") in references
    assert ("Device", "123") in references


def test_extract_resource_ids(server):

    conditions = server.query("Condition").include(resource="Condition", reference_param="subject").all()

    resource_ids = _resource_ids_from_query_response(conditions)
    assert len(resource_ids["Condition"]) == len(conditions.resources)
    assert len(resource_ids["Patient"]) == len(conditions.included_resources[0].resources)


def test_validate_references(server):

    conditions = server.query("Condition").include(resource="Condition", reference_param="subject").all()
    result = validate_references(conditions)

    assert len(result) == 0

    conditions = server.query("Condition").all()
    result = validate_references(conditions)

    assert len(result) == len(conditions.resources)

