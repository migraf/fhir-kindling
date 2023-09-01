import os
from unittest import mock

import pytest
from dotenv import find_dotenv, load_dotenv
from fhir.resources import FHIRAbstractModel
from fhir.resources.address import Address
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient
from fhir.resources.reference import Reference
from httpx import BasicAuth, HTTPStatusError

from fhir_kindling import FhirQuerySync, FhirServer
from fhir_kindling.fhir_query import FhirQueryParameters
from fhir_kindling.generators import PatientGenerator
from fhir_kindling.serde.json import json_dict


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
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL"),
    )
    return server


@pytest.fixture
def fhir_server(api_url):
    print(api_url)
    server = FhirServer(
        api_address=api_url,
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL"),
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
            **{"method": "POST", "url": org.get_resource_type()}
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


@pytest.mark.asyncio
async def test_server_summary_async(fhir_server: FhirServer):
    summary = await fhir_server.summary_async(display=False)
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
        },
    ):
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
        },
    ):
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
        },
    ):
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
        },
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
        },
    ):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()

    # conflicting auth user and client_id/secret
    with mock.patch.dict(
        os.environ,
        {
            "FHIR_API_URL": "http://test.fhir.org/r4",
            "FHIR_USER": "user",
            "FHIR_PW": "password",
            "CLIENT_ID": "token",
        },
    ):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()

    # conflicting auth token and client_id/secret
    with mock.patch.dict(
        os.environ,
        {
            "FHIR_API_URL": "http://test.fhir.org/r4",
            "CLIENT_ID": "token",
            "FHIR_TOKEN": "token",
        },
    ):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()

    # missing client secret & provider url
    with mock.patch.dict(
        os.environ,
        {
            "FHIR_API_URL": "http://test.fhir.org/r4",
            "CLIENT_ID": "token",
            "CLIENT_SECRET": "",
        },
    ):
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
        },
    ):
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
        },
    ):
        with pytest.raises(EnvironmentError):
            server = FhirServer.from_env()

    print(client_id, client_secret, oidc_provider_url)
    # with mock.patch.dict(
    #         os.environ,
    #         {
    #             "FHIR_API_URL": "http://test.fhir.org/r4",
    #             "CLIENT_ID": "client",
    #             "CLIENT_SECRET": "secret",
    #             "OIDC_PROVIDER_URL": "url",
    #             "FHIR_USER": "",
    #             "FHIR_PW": "",
    #             "FHIR_TOKEN": ""
    #         }
    # ):
    #     server = FhirServer.from_env()


def test_server_query_validation(fhir_server: FhirServer):
    params = FhirQueryParameters(
        resource="Patient",
    )

    # test invalid query resource + params
    with pytest.raises(ValueError):
        fhir_server.query(resource="Patient", query_parameters=params)

    with pytest.raises(ValueError):
        fhir_server.query(query_string="Patient?", query_parameters=params)

    with pytest.raises(ValueError):
        fhir_server.query(query_string="Patient?", resource="Patient")

    with pytest.raises(ValueError):
        fhir_server.query()


def test_upload_single_resource(fhir_server: FhirServer):
    from fhir.resources.address import Address
    from fhir.resources.organization import Organization

    org = Organization.construct()
    org.name = "Test Create Org"
    address = Address.construct()
    address.country = "Germany"
    org.address = [address]

    Organization.element_properties()

    response = fhir_server.add(org)

    response2 = fhir_server.add(org.dict())

    assert response2

    with pytest.raises(ValueError):
        fhir_server.add({"dshadk": "sjdhka"})

    assert response


def test_server_add_all(fhir_server: FhirServer):
    generator = PatientGenerator(n=100)
    patients = generator.generate()
    add_response = fhir_server.add_all(patients)

    assert add_response

    batched_add_response = fhir_server.add_all(patients, batch_size=10)

    assert len(batched_add_response.create_responses) == 100


def test_query_all(fhir_server: FhirServer):
    response = fhir_server.query(Patient.construct(), output_format="json").all()
    assert response.response


def test_query_with_string_resource(fhir_server: FhirServer):
    auth = fhir_server.auth
    query = FhirQuerySync(fhir_server.api_address, "Patient", auth=auth)

    response = query.all()

    assert isinstance(query.resource, FHIRAbstractModel)

    assert response


def test_query_with_limit(fhir_server: FhirServer):
    response = fhir_server.query(Patient.construct(), output_format="json").limit(2)

    assert response.response["entry"]

    assert len(response.response["entry"]) == 2


def test_query_raw_string(fhir_server: FhirServer):
    query_string = "/Patient?"
    query = fhir_server.raw_query(query_string=query_string, output_format="json")

    query_2 = fhir_server.query(query_string=query_string, output_format="json")

    assert isinstance(query, FhirQuerySync)

    assert query.resource.get_resource_type() == "Patient"

    assert query.all().response["entry"]

    assert query_2.query_parameters.resource == "Patient"


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

    resource_reference = add_response.references[51]
    fhir_server.delete(resources=add_response.resources[50:75])

    with pytest.raises(HTTPStatusError):
        fhir_server.get(resource_reference)

    # fhir_server.delete(resources=[r.dict() for r in add_response.resources[75:]])

    # with pytest.raises(ValueError):
    #     fhir_server.delete(resources=["asd"], references=["asd"])
    # with pytest.raises(ValueError):
    #     fhir_server.delete(resources=["asd"], query=["asd"])

    # with pytest.raises(ValueError):
    #     fhir_server.delete(references=["asd"], query=["asd"])


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


def test_custom_headers():
    headers = {"X-Custom-Header": "Test", "X-Custom-Header2": "Test2"}
    server = FhirServer(api_address="https://fhir.test/fhir", headers=headers)

    assert server.headers["X-Custom-Header"] == "Test"
    assert server.headers["X-Custom-Header2"] == "Test2"
    assert server.headers["Content-Type"] == "application/fhir+json"


def test_custom_auth():
    auth = BasicAuth(username="test", password="test")
    server = FhirServer(api_address="https://fhir.test/fhir", auth=auth)

    assert server._auth == auth

    # with pytest.raises(ValueError):
    #     server = FhirServer(api_address="https://fhir.test/fhir", auth=auth, username="test")
    #
    # with pytest.raises(ValueError):
    #     server = FhirServer(api_address="https://fhir.test/fhir", auth=auth, token="test")
    #
    # with pytest.raises(ValueError):
    #     server = FhirServer(api_address="https://fhir.test/fhir", auth=auth, client_id="test")


def test_query_with_params(fhir_server: FhirServer):
    params = FhirQueryParameters(resource="Condition")
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


def test_transfer(fhir_server: FhirServer):
    api_url = os.getenv("FHIR_API_URL", "http://localhost:9090/fhir")
    server = FhirServer(api_address=api_url, timeout=None)
    conditions = server.query("Condition")
    transfer_url = os.getenv("TRANSFER_SERVER_URL", "http://localhost:9091/fhir")
    hapi_server = FhirServer(api_address=transfer_url, timeout=None)

    # conditions_before = hapi_server.query("Condition").all().resources

    response = server.transfer(hapi_server, query=conditions)

    assert response


@pytest.mark.asyncio
async def test_fhir_server_get_async(fhir_server: FhirServer):
    patient_gen = PatientGenerator(n=1)
    patient = patient_gen.generate()[0]
    patient_create = fhir_server.add(patient)

    patient = await fhir_server.get_async(patient_create.reference)
    assert patient
    assert patient.id == patient_create.resource_id


@pytest.mark.asyncio
async def test_fhir_server_add_async(fhir_server: FhirServer):
    patient_gen = PatientGenerator(n=1)
    patient = patient_gen.generate()[0]
    patient_create = await fhir_server.add_async(patient)

    assert patient_create
    assert patient_create.resource_id

    patient_dict = json_dict(patient)
    patient_create_dict = await fhir_server.add_async(patient_dict)

    assert patient_create_dict

    patient_dict["resourceType"] = None
    with pytest.raises(ValueError):
        await fhir_server.add_async(patient_dict)


@pytest.mark.asyncio
async def test_fhir_server_add_all_async(fhir_server: FhirServer):
    patient_gen = PatientGenerator(n=100)
    patients = patient_gen.generate()
    patients_create = await fhir_server.add_all_async(patients)
    assert patients_create

    batched_add_response = await fhir_server.add_all_async(patients, batch_size=10)

    assert len(batched_add_response.create_responses) == 100


@pytest.mark.asyncio
async def test_fhir_server_get_many_async(fhir_server: FhirServer):
    patients = fhir_server.query("Patient").limit(10)
    references = [p.relative_path() for p in patients.resources]
    patients = await fhir_server.get_many_async(references)
    assert len(patients) == 10


@pytest.mark.asyncio
async def test_fhir_server_query_async(fhir_server: FhirServer):
    query = fhir_server.query_async(Patient.construct(), output_format="json")
    response = await query.all()
    assert response

    parameters = FhirQueryParameters(
        resource="Patient",
    )
    query = fhir_server.query_async(query_parameters=parameters)
    response = await query.limit(10)
    assert response

    query = fhir_server.query_async(query_string="/Patient?")
    response = await query.limit(10)
    assert response


@pytest.mark.asyncio
async def test_add_bundle_async(fhir_server: FhirServer, org_bundle):
    response = await fhir_server.add_bundle_async(org_bundle)
    assert response


@pytest.mark.asyncio
async def test_fhir_server_query_raw_async(fhir_server: FhirServer):
    query_string = "/Patient?"
    query = fhir_server.raw_query_async(query_string=query_string, output_format="json")
    response = await query.all()
    assert response


@pytest.mark.asyncio
async def test_update_async(fhir_server: FhirServer):
    # create 100 patients
    generator = PatientGenerator(n=2)
    patients = generator.generate()
    add_response = fhir_server.add_all(patients)
    print(add_response.references)

    # update the first patient
    patient = add_response.resources[0]
    patient.name[0].family = "Test"
    update_response = await fhir_server.update_async([patient])
    print(update_response)

    patient.name[0].family = "Test2"
    update_response = await fhir_server.update_async([patient.dict()])

    # no resource type in dict
    with pytest.raises(ValueError):
        update_response = await fhir_server.update_async([{"dsada": "asdas"}])

    # invalid resource type
    with pytest.raises(ValueError):
        update_response = await fhir_server.update_async(["sdjhadk"])


@pytest.mark.asyncio
async def test_delete_async(fhir_server: FhirServer):
    # create 100 patients
    generator = PatientGenerator(n=100)
    patients = generator.generate()
    add_response = fhir_server.add_all(patients)

    await fhir_server.delete_async(references=add_response.references[:50])

    await fhir_server.delete_async(resources=add_response.resources[50:75])
    # await fhir_server.delete_async(
    #     resources=[r.dict() for r in add_response.resources[75:]]
    # )

    delete_reference = add_response.references[15]
    with pytest.raises(HTTPStatusError):
        await fhir_server.get_async(delete_reference)

    # with pytest.raises(ValueError):
    #     await fhir_server.delete_async(resources=["asd"], references=["asd"])
    # with pytest.raises(ValueError):
    #     await fhir_server.delete_async(resources=["asd"], query=["asd"])

    # with pytest.raises(ValueError):
    #     await fhir_server.delete_async(references=["asd"], query=["asd"])
