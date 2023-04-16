import os
from unittest import mock

import pytest
from httpx import Auth

from fhir_kindling.fhir_server.auth import (
    BearerAuth,
    generate_auth,
    load_environment_auth_vars,
)


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
