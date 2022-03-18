import os
import uuid

import pytest
from fhir.resources import FHIRAbstractModel
from unittest import mock

from fhir.resources.condition import Condition
from fhir.resources.encounter import Encounter
from fhir.resources.reference import Reference
from requests.auth import HTTPBasicAuth

from fhir_kindling import FhirServer, FHIRQuery
from dotenv import load_dotenv, find_dotenv
from fhir.resources.organization import Organization
from fhir.resources.address import Address
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.patient import Patient

from fhir_kindling.fhir_query import FHIRQueryParameters
from fhir_kindling.generators import PatientGenerator
from fhir_kindling.util.references import reference_graph


@pytest.fixture
def api_url():
    """
    Base api url and env vars
    """
    load_dotenv(find_dotenv())

    return os.getenv("FHIR_API_URL", "http://test.fhir.org/r4")


@pytest.fixture
def oidc_server(api_url):
    server = FhirServer(
        api_address=api_url,
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL")
    )
    return server


@pytest.fixture
def fhir_server(api_url):
    print(api_url)
    server = FhirServer(
        api_address=api_url,
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL")
    )
    return server


@pytest.fixture
def org_bundle(api_url):
    bundle = Bundle.construct()
    bundle.type = "transaction"

    entries = []

    for i in range(10):
        org = Organization.construct()
        org.name = f"Test Create Org No. {i}"
        address = Address.construct()
        address.country = "Germany"
        org.address = [address]

        entry = BundleEntry.construct()

        entry.request = BundleEntryRequest(
            **{
                "method": "POST",
                "url": org.get_resource_type()
            }
        )

        entry.resource = org.dict()
        entries.append(entry)

    bundle.entry = entries
    return bundle


def test_server_api_url_validation(api_url):
    server = FhirServer(api_address=api_url)

    assert server
    malformed_url_1 = "hello-world"

    with pytest.raises(ValueError):
        server = FhirServer(api_address=malformed_url_1)

    malformed_url_2 = "htp://hapi.fhir.org/baseR4"
    with pytest.raises(ValueError):
        server = FhirServer(api_address=malformed_url_2)

    server = FhirServer(api_address="http://blaze:8080/fhir")
    assert server

    server = FhirServer(api_address="http://bla_ze:8080/fhir")
    assert server

    server = FhirServer(api_address="http://bla-ze:8080/fhir")
    assert server

    with pytest.raises(ValueError):
        server = FhirServer(api_address="http://bla ze:8080/fhir")

    with pytest.raises(ValueError):
        server = FhirServer(api_address="http://bla_ze:8080/ fhir")

    with pytest.raises(ValueError):
        server = FhirServer(api_address="http://bla_ze:8x80/fhir")


def test_server_capabilities(fhir_server):
    capabilities = fhir_server.capabilities
    assert capabilities


def test_server_rest_resources(fhir_server: FhirServer):
    resources = fhir_server.rest_resources
    assert resources
    assert len(resources) > 1


def test_server_summary(fhir_server: FhirServer):
    summary = fhir_server.summary()
    assert summary
    print(summary)


def test_fhir_server_from_env():
    load_dotenv(find_dotenv())

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    oidc_provider_url = os.getenv("OIDC_PROVIDER_URL")

    with mock.patch.dict(os.environ, {"FHIR_API_URL": "http://test.fhir.org/r4"}):
        server = FhirServer.from_env(no_auth=True)
        assert server
    with mock.patch.dict(
            os.environ,
            {
                "FHIR_API_URL": "http://test.fhir.org/r4",
                "FHIR_USER": "",
                "FHIR_PW": "",
                "FHIR_TOKEN": "",
                "CLIENT_ID": "",
                "CLIENT_SECRET": "",
            }):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()

    # user and no password in env
    with mock.patch.dict(
            os.environ,
            {
                "FHIR_API_URL": "http://test.fhir.org/r4",
                "FHIR_USER": "user",
                "FHIR_PW": "",
                "FHIR_TOKEN": "",
                "CLIENT_ID": "",
                "CLIENT_SECRET": "",
            }):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()

    # correct basic auth config
    with mock.patch.dict(
            os.environ,
            {
                "FHIR_API_URL": "http://test.fhir.org/r4",
                "FHIR_USER": "user",
                "FHIR_PW": "password",
                "FHIR_TOKEN": "",
                "CLIENT_ID": "",
                "CLIENT_SECRET": "",
            }):
        server = FhirServer.from_env()
        assert server.auth

    # token auth
    with mock.patch.dict(
            os.environ,
            {
                "FHIR_API_URL": "http://test.fhir.org/r4",
                "FHIR_TOKEN": "token",
                "CLIENT_ID": "",
                "CLIENT_SECRET": "",
                "FHIR_USER": "",
                "FHIR_PW": "",
            }
    ):
        server = FhirServer.from_env()
        assert server.auth

    # conflicting auth token and user/password
    with mock.patch.dict(
            os.environ,
            {
                "FHIR_API_URL": "http://test.fhir.org/r4",
                "FHIR_USER": "user",
                "FHIR_PW": "password",
                "FHIR_TOKEN": "token",
                "CLIENT_ID": "",
                "CLIENT_SECRET": "",
            }):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()

    # conflicting auth user and client_id/secret
    with mock.patch.dict(
            os.environ,
            {
                "FHIR_API_URL": "http://test.fhir.org/r4",
                "FHIR_USER": "user",
                "FHIR_PW": "password",
                "CLIENT_ID": "token"
            }):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()

    # conflicting auth token and client_id/secret
    with mock.patch.dict(
            os.environ,
            {
                "FHIR_API_URL": "http://test.fhir.org/r4",
                "CLIENT_ID": "token",
                "FHIR_TOKEN": "token"
            }):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()

    # missing client secret & provider url
    with mock.patch.dict(
            os.environ,
            {
                "FHIR_API_URL": "http://test.fhir.org/r4",
                "CLIENT_ID": "token",
                "CLIENT_SECRET": "",
            }):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()

    # missing provider url
    with mock.patch.dict(
            os.environ,
            {
                "FHIR_API_URL": "http://test.fhir.org/r4",
                "CLIENT_ID": "token",
                "CLIENT_SECRET": "token",
                "OIDC_PROVIDER_URL": "",
            }):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()
    # missing secret
    with mock.patch.dict(
            os.environ,
            {
                "FHIR_API_URL": "http://test.fhir.org/r4",
                "CLIENT_ID": "token",
                "OIDC_PROVIDER_URL": "https://test.fhir.org/r4",
                "CLIENT_SECRET": "",
            }):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()

    print(client_id, client_secret, oidc_provider_url)
    with mock.patch.dict(
            os.environ,
            {
                "FHIR_API_URL": "http://test.fhir.org/r4",
                "CLIENT_ID": client_id,
                "CLIENT_SECRET": client_secret,
                "OIDC_PROVIDER_URL": oidc_provider_url,
                "FHIR_USER": "",
                "FHIR_PW": "",
                "FHIR_TOKEN": ""
            }):
        server = FhirServer.from_env()


def test_upload_single_resource(fhir_server: FhirServer):
    from fhir.resources.organization import Organization
    from fhir.resources.address import Address

    org = Organization.construct()
    org.name = "Test Create Org"
    address = Address.construct()
    address.country = "Germany"
    org.address = [address]

    Organization.element_properties()

    response = fhir_server.add(org)

    response2 = fhir_server.add(org.dict())

    with pytest.raises(ValueError):
        fhir_server.add({"dshadk": "sjdhka"})

    assert response


def test_server_add_all(fhir_server: FhirServer):
    generator = PatientGenerator(n=100)
    patients = generator.generate()
    add_response = fhir_server.add_all(patients)

    assert add_response


def test_query_all(fhir_server: FhirServer):
    response = fhir_server.query(Patient.construct(), output_format="dict").all()
    print(response)
    assert response.response


def test_query_with_string_resource(fhir_server: FhirServer):
    auth = fhir_server.auth
    query = FHIRQuery(fhir_server.api_address, "Patient", auth=auth)

    response = query.all()

    assert isinstance(query.resource, FHIRAbstractModel)

    assert response


def test_query_with_limit(fhir_server: FhirServer):
    response = fhir_server.query(Patient.construct(), output_format="dict").limit(2)

    assert response.response["entry"]

    assert len(response.response["entry"]) == 2


def test_query_raw_string(fhir_server: FhirServer):
    query_string = "/Patient?"
    query = fhir_server.raw_query(query_string=query_string, output_format="dict")

    assert isinstance(query, FHIRQuery)

    assert query.resource.get_resource_type() == "Patient"

    assert query.all().response["entry"]


def test_add_bundle(fhir_server: FhirServer, org_bundle):
    response = fhir_server.add_bundle(org_bundle)
    assert response
    print(response)


def test_delete(fhir_server: FhirServer):
    # create 100 patients
    generator = PatientGenerator(n=100)
    patients = generator.generate()
    add_response = fhir_server.add_all(patients)
    print(add_response.references)

    delete_response = fhir_server.delete(references=add_response.references[:50])
    print(delete_response)

    delete_resource = fhir_server.delete(resources=add_response.resources[50:75])
    print(delete_resource)
    assert delete_resource
    delete_resource = fhir_server.delete(resources=[r.dict() for r in add_response.resources[75:]])
    assert delete_resource
    print(delete_resource)

    with pytest.raises(ValueError):
        fhir_server.delete(resources=["asd"], references=["asd"])
    with pytest.raises(ValueError):
        fhir_server.delete(resources=["asd"], query=["asd"])

    with pytest.raises(ValueError):
        fhir_server.delete(references=["asd"], query=["asd"])


def test_update(fhir_server: FhirServer):
    # create 100 patients
    generator = PatientGenerator(n=2)
    patients = generator.generate()
    add_response = fhir_server.add_all(patients)
    print(add_response.references)

    # update the first patient
    patient = add_response.resources[0]
    patient.name[0].family = "Test"
    update_response = fhir_server.update([patient])
    print(update_response)

    patient.name[0].family = "Test2"
    update_response = fhir_server.update([patient.dict()])

    # no resource type in dict
    with pytest.raises(ValueError):
        update_response = fhir_server.update([{"dsada": "asdas"}])

    # invalid resource type
    with pytest.raises(ValueError):
        update_response = fhir_server.update(["sdjhadk"])


# def test_transfer(fhir_server: FhirServer):
#     origin_server = FhirServer(api_address="https://mii-agiop-cord.life.uni-leipzig.de/fhir")
#     query = origin_server.query("Condition").all()
#     print(query.resources)

def test_custom_headers():
    headers = {"X-Custom-Header": "Test", "X-Custom-Header2": "Test2"}
    server = FhirServer(api_address="https://fhir.test/fhir", headers=headers)

    assert server.session.headers["X-Custom-Header"] == "Test"
    assert server.session.headers["X-Custom-Header2"] == "Test2"
    assert server.session.headers["Content-Type"] == "application/fhir+json"


def test_custom_auth():
    auth = HTTPBasicAuth(username="test", password="test")
    server = FhirServer(api_address="https://fhir.test/fhir", auth=auth)

    assert server.session.auth == auth

    with pytest.raises(ValueError):
        server = FhirServer(api_address="https://fhir.test/fhir", auth=auth, username="test")

    with pytest.raises(ValueError):
        server = FhirServer(api_address="https://fhir.test/fhir", auth=auth, token="test")

    with pytest.raises(ValueError):
        server = FhirServer(api_address="https://fhir.test/fhir", auth=auth, client_id="test")


def test_query_with_params(fhir_server: FhirServer):
    params = FHIRQueryParameters(
        resource="Condition"
    )
    query = fhir_server.query(query_parameters=params)
    response = query.all()

    assert response.resources


def test_fhir_server_get(fhir_server: FhirServer):
    patient = fhir_server.query("Patient").first().resources[0]

    patient_by_reference = fhir_server.get(patient.relative_path())

    assert patient_by_reference.id == patient.id


def test_fhir_server_get_many(fhir_server: FhirServer):
    patients = fhir_server.query("Patient").limit(10).resources

    references = [p.relative_path() for p in patients]
    patients_by_reference = fhir_server.get_many(references)

    assert len(patients_by_reference) == len(patients)

    for p, p2 in zip(patients, patients_by_reference):
        assert p.id == p2.id


def test_server_repr_str(fhir_server: FhirServer):
    print(fhir_server)
    assert fhir_server.__repr__() == fhir_server.__str__()


def test_get(oidc_server: FhirServer):
    response = oidc_server.query("Patient").first()
    patient = oidc_server.get(f"Patient/{response.resources[0].id}")
    assert patient
    assert patient.id == response.resources[0].id

    reference = Reference(reference=f"Patient/{response.resources[0].id}")
    patient = oidc_server.get(reference)

    assert patient
    assert patient.id == response.resources[0].id


def test_get_many(fhir_server: FhirServer):
    patients = fhir_server.query("Patient").limit(10)
    references = [p.relative_path() for p in patients.resources]
    patients = fhir_server.get_many(references)
    assert len(patients) == 10


def test_resolve_reference_graph(fhir_server: FhirServer):
    patients, patient_references = PatientGenerator(n=10, generate_ids=True).generate(references=True)
    organization = Organization(name="Test", id="test-org")
    practitioner = Organization(name="Practitioner", id="test-practitioner")
    conditions = []
    encounter = Encounter(
        **{
            "id": "test-encounter",
            "status": "planned",
            "class": {"code": "AMB", "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"}
        }
    )
    for patient in patients:
        patient.managingOrganization = {"reference": organization.relative_path()}
        patient.generalPractitioner = [{"reference": practitioner.relative_path()}]
        condition = Condition(subject={"reference": patient.relative_path()}, id=str(uuid.uuid4()))
        condition.encounter = {"reference": encounter.relative_path()}
        conditions.append(condition)

    resources = patients + [organization, practitioner, encounter] + conditions
    # print(resources)

    hapi_server = FhirServer(api_address="http://localhost:8082/fhir")
    response = fhir_server._transfer_resources(hapi_server, resources)


def test_fhir_server_transfer(fhir_server: FhirServer):
    conditions = fhir_server.query("Condition").limit(10)
    hapi_server = FhirServer(api_address="http://localhost:8082/fhir")
    response = fhir_server.transfer(hapi_server, conditions)

    print(response)
    assert response.destination_server == hapi_server.api_address
    assert len(response.create_responses) >= 10
