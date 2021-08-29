import pytest
import requests
from requests.auth import HTTPBasicAuth

from fhir_kindling.query import query, query_resource, query_with_string
from fhir.resources.procedure import Procedure
from fhir_kindling.upload import generate_fhir_headers


@pytest.fixture
def api_url():
    """
    Base api url

    """
    return "http://hapi.fhir.org/baseR4"

@pytest.fixture
def bogus_auth():
    """
    Lower level functions expect auth information to be given. The public test server does not require but it needs to
    be present.
    Returns:

    """

    return HTTPBasicAuth(username="bogus", password="auth")

@pytest.fixture
def fhir_headers():
    return generate_fhir_headers(fhir_server_type="hapi")


def test_api_connection(api_url):
    url = api_url + "/metadata"
    r = requests.get(url)

    r.raise_for_status()
    assert r.text


def test_query_resource(api_url, bogus_auth, fhir_headers):

    limit = 100
    response = query_resource("Procedure", fhir_server_url=api_url, auth=bogus_auth, headers=fhir_headers, limit=limit)
    assert response
    assert len(response["entry"]) == limit

    response2 = query_resource(Procedure, fhir_server_url=api_url, auth=bogus_auth, headers=fhir_headers, limit=limit)
    assert response == response2





