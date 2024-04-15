import os
from unittest import mock

import pytest
from httpx import Auth

from fhir_kindling import FhirServer
from fhir_kindling.fhir_server.auth import (
    BearerAuth,
    OIDCAuth,
    generate_auth,
    load_environment_auth_vars,
)


def test_oidc_auth():
    client_id = os.getenv("KINDLING_CLIENT_ID")
    client_secret = os.getenv("KINDLING_CLIENT_SECRET")
    oidc_provider_url = os.getenv("OIDC_PROVIDER_URL")
    oidc_auth = OIDCAuth(
        oidc_provider_url=oidc_provider_url,
        client_id=client_id,
        client_secret=client_secret,
    )

    assert isinstance(oidc_auth, OIDCAuth)
    token = oidc_auth.get_token()
    assert isinstance(token, str)


def test_query_with_oidc_auth():
    client_id = os.getenv("KINDLING_CLIENT_ID")
    client_secret = os.getenv("KINDLING_CLIENT_SECRET")
    oidc_provider_url = os.getenv("OIDC_PROVIDER_URL")
    # oidc_server_url = os.getenv("OIDC_SERVER_URL")
    oidc_server_url = "http://127.0.0.1:9092/fhir"
    oidc_server = FhirServer(
        api_address=oidc_server_url,
        client_id=client_id,
        client_secret=client_secret,
        oidc_provider_url=oidc_provider_url,
    )

    assert isinstance(oidc_server, FhirServer)
    response = oidc_server.query("Patient").all()
    assert response


def test_generate_auth():
    basic_auth = generate_auth(username="basic", password="auth")

    assert isinstance(basic_auth, Auth)

    bearer_auth = generate_auth(token="test_token")

    assert isinstance(bearer_auth, BearerAuth)

    # Conflicting auth information should raise an error
    with pytest.raises(ValueError):
        generate_auth(username="test", password="conflicting", token="auth")

    # No auth information should give an error
    with pytest.raises(ValueError):
        generate_auth()
    with pytest.raises(ValueError):
        generate_auth(username="test")


@mock.patch.dict(
    os.environ, {"FHIR_USER": "test", "FHIR_PW": "password", "FHIR_TOKEN": "fhir-token"}
)
def test_load_env_var_auth():
    username, password, token = load_environment_auth_vars()

    assert username == "test"
    assert password == "password"
    assert token == "fhir-token"


@mock.patch.dict(
    os.environ, {"FHIR_USER": "test", "FHIR_PW": "password", "FHIR_TOKEN": "fhir-token"}
)
def test_env_var_conflicts():
    with pytest.raises(ValueError):
        generate_auth(load_env=True)


@mock.patch.dict(os.environ, {"FHIR_USER": "test", "FHIR_PW": "password"})
def test_env_var_basic():
    basic_auth = generate_auth(load_env=True)
    assert isinstance(basic_auth, Auth)
