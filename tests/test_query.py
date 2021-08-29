import pytest
import requests
from requests.auth import HTTPBasicAuth

from fhir_kindling.query import query, query_resource, query_with_string
from fhir.resources.procedure import Procedure
from fhir_kindling.upload import generate_fhir_headers
from fhir_kindling.auth import generate_auth


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

    token_auth = generate_auth(token="test_token")
    response2 = query_resource(Procedure, fhir_server_url=api_url, auth=token_auth, headers=fhir_headers, limit=limit)
    assert response == response2

    # test paginated responses
    response3 = query_resource("Procedure", fhir_server_url=api_url, auth=bogus_auth, headers=fhir_headers, limit=2500)
    assert len(response3["entry"]) == 2500


def test_query_with_string(api_url, bogus_auth, fhir_headers):
    # simple query for patients by age
    query_string_1 = "Patient?birthdate=gt1990"

    response_1 = query_with_string(query_string_1, api_url, bogus_auth, fhir_headers, limit=100)

    assert response_1
    assert len(response_1["entry"]) == 100

    # test that / mismatch is resolved
    query_string_2 = "/Observation?patient.birthdate=gt1990"
    response_2 = query_with_string(query_string_2, api_url + "/", bogus_auth, fhir_headers, limit=100)

    assert response_2


def test_query(api_url, bogus_auth, fhir_headers):
    query_string = "/Observation?patient.birthdate=gt1990"

    response = query(query_string=query_string, limit=100, username="test", password="password",
                     fhir_server_url=api_url, fhir_server_type="hapi")

    assert response





