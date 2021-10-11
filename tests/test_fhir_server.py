import os

import pytest
from fhir.resources import FHIRAbstractModel

from fhir_kindling import FhirServer, FHIRQuery
from dotenv import load_dotenv, find_dotenv
from fhir.resources.organization import Organization
from fhir.resources.address import Address


@pytest.fixture
def api_url():
    """
    Base api url and env vars
    """
    load_dotenv(find_dotenv())

    return os.getenv("FHIR_API_URL", "http://hapi.fhir.org/baseR4")


@pytest.fixture
def oidc_server(api_url):
    server = FhirServer(
        api_address=api_url,
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL")
    )
    return server


def test_server_api_url_validation(api_url):
    server = FhirServer(api_address=api_url)

    malformed_url_1 = "hello-world"

    with pytest.raises(ValueError):
        server = FhirServer(api_address=malformed_url_1)

    malformed_url_2 = "htp://hapi.fhir.org/baseR4"
    with pytest.raises(ValueError):
        server = FhirServer(api_address=malformed_url_2)


def test_oidc_auth_server(api_url):
    server = FhirServer(
        api_address=api_url,
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL")
    )

    assert server.auth


def test_server_capabilities(oidc_server):
    capabilities = oidc_server.capabilities
    assert capabilities


def test_upload_single_resource(oidc_server: FhirServer):
    from fhir.resources.organization import Organization
    from fhir.resources.address import Address

    org = Organization.construct()
    org.name = "Test Create Org"
    address = Address.construct()
    address.country = "Germany"
    org.address = [address]

    Organization.element_properties()

    response = oidc_server.add(org)

    print(response.resource)

    assert response


def test_query_all(oidc_server: FhirServer):
    response = oidc_server.query(Organization).all()

    assert response["entry"]


def test_query_with_string_resource(oidc_server: FhirServer):
    auth = oidc_server.auth
    query = FHIRQuery(oidc_server.api_address, "Patient", auth=auth)

    response = query.all()

    assert isinstance(query.resource, FHIRAbstractModel)

    assert response


def test_query_with_limit(oidc_server: FhirServer):
    response = oidc_server.query(Organization).limit(2)

    assert response["entry"]

    assert len(response["entry"]) == 2
