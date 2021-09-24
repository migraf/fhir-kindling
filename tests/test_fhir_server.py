import pytest

from fhir_kindling import FhirServer


@pytest.fixture
def api_url():
    """
    Base api url
    """
    return "http://hapi.fhir.org/baseR4"


def test_server_api_url_validation(api_url):

    server = FhirServer(api_address=api_url)

    malformed_url_1 = "hello-world"

    with pytest.raises(ValueError):
        server = FhirServer(api_address=malformed_url_1)

    malformed_url_2 = "htp://hapi.fhir.org/baseR4"
    with pytest.raises(ValueError):
        server = FhirServer(api_address=malformed_url_2)


def test_server_capabilities(api_url):
    server = FhirServer(api_url, username="test", password="test")
    capabilities = server.meta_data()

