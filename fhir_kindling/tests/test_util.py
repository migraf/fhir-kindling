import os
import uuid

import pytest
from dotenv import find_dotenv, load_dotenv
from fhir.resources.condition import Condition
from fhir.resources.encounter import Encounter
from fhir.resources.observation import Observation
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient

from fhir_kindling import FhirServer
from fhir_kindling.benchmark.bench import ServerBenchmark
from fhir_kindling.fhir_server.transfer import reference_graph
from fhir_kindling.generators import PatientGenerator
from fhir_kindling.util.references import (
    _resource_ids_from_query_response,
    check_missing_references,
    extract_references,
)
from fhir_kindling.util.resources import (
    check_resource_contains_field,
    get_resource_fields,
)


@pytest.fixture
def server():
    load_dotenv(find_dotenv())
    server = FhirServer(
        api_address=os.getenv("FHIR_API_URL"),
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL"),
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
    print(obs)
    references = extract_references(obs)
    assert len(references) == 3

    assert ("subject", "Patient", "123", False) in references
    assert ("specimen", "Specimen", "123", False) in references
    assert ("device", "Device", "123", False) in references


def test_extract_resource_ids(server):
    conditions = (
        server.query("Condition")
        .include(resource="Condition", reference_param="subject")
        .all()
    )

    resource_ids = _resource_ids_from_query_response(conditions)
    assert len(resource_ids["Condition"]) == len(conditions.resources)
    assert len(resource_ids["Patient"]) == len(
        conditions.included_resources[0].resources
    )


def test_check_missing_references(server):
    conditions = (
        server.query("Condition")
        .include(resource="Condition", reference_param="subject")
        .all()
    )
    resources = conditions.resources
    resources.extend(conditions.included_resources[0].resources)
    no_missing = check_missing_references(resources)
    print(no_missing)

    assert len(no_missing) == 0

    conditions = server.query("Condition").all()

    missing = check_missing_references(conditions.resources)

    assert len(missing) == len(conditions.resources)


def test_reference_graph():
    # create inter-referenced resources
    patients, patient_references = PatientGenerator(n=10, generate_ids=True).generate(
        references=True
    )
    organization = Organization(name="Test", id="test-org")
    practitioner = Organization(name="Practitioner", id="test-practitioner")
    conditions = []
    encounter = Encounter(
        **{
            "id": "test-encounter",
            "status": "planned",
            "class": {
                "code": "AMB",
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            },
        }
    )
    for patient in patients:
        patient.managingOrganization = {"reference": organization.relative_path()}
        patient.generalPractitioner = [{"reference": practitioner.relative_path()}]
        condition = Condition(
            subject={"reference": patient.relative_path()}, id=str(uuid.uuid4())
        )
        condition.encounter = {"reference": encounter.relative_path()}
        conditions.append(condition)

    resources = patients + [organization, practitioner, encounter] + conditions
    graph = reference_graph(resources)

    for node in graph.nodes:
        # print(node["resource"])
        print(graph.nodes[node]["resource"])

    assert len(graph.nodes) == len(resources)
    assert len(list(graph.predecessors(organization.relative_path()))) == 0
    assert len(list(graph.predecessors(conditions[0].relative_path()))) == 2


def test_resource_contains_field(server):
    check_resource_contains_field("Patient", "birthDate")
    with pytest.raises(ValueError):
        check_resource_contains_field("Patient", "foo")


def test_benchmark(server):
    transfer_server = FhirServer(api_address=os.getenv("TRANSFER_SERVER_URL"))
    benchmark = ServerBenchmark(
        servers=[server, transfer_server], n_attempts=2, dataset_size=10
    )
    benchmark.run_suite(progress=False, save=False)
    # benchmark.plot()


def test_retry_transport():
    wrong_server_url = os.getenv("FHIR_API_URL") + "foo"
    transfer_server = FhirServer(
        api_address=wrong_server_url, retry_status_codes=[404], max_atttempts=3
    )

    with pytest.raises(Exception):
        transfer_server.query("Patient").all()
