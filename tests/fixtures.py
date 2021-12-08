import pytest
import os
from dotenv import load_dotenv, find_dotenv

from fhir_kindling import FhirServer


@pytest.fixture
def api_url():
    """
    Base api url and env vars
    """
    load_dotenv(find_dotenv())

    return os.getenv("FHIR_API_URL", "http://test.fhir.org/r4")


@pytest.fixture
def oidc_server(api_url):
    print(api_url)
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
