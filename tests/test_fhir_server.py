import os

import pytest

from fhir_kindling import FhirServer
from dotenv import load_dotenv, find_dotenv


@pytest.fixture
def api_url():
    """
    Base api url and env vars
    """
    load_dotenv(find_dotenv())

    return os.getenv("FHIR_API_URL", "http://hapi.fhir.org/baseR4")


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

    assert server.capabilities



def test_server_capabilities(api_url):
    server = FhirServer(api_url, username="test", password="test")
    capabilities = server.capabilities
