import os

import pandas as pd
import pytest
from dotenv import find_dotenv, load_dotenv

from fhir_kindling import FhirServer
from fhir_kindling.serde.flatten import (
    flatten_resource,
    flatten_resources,
    flatten_response,
)


@pytest.fixture
def api_url():
    """
    Base api url and env vars
    """
    load_dotenv(find_dotenv())

    return os.getenv("FHIR_API_URL", "http://test.fhir.org/r4")


@pytest.fixture
def server(api_url):
    server = FhirServer(
        api_address=api_url,
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL"),
    )
    return server


def test_flatten(server):
    query_resource = "Condition"
    search_param = "subject"
    query = server.query("Patient")
    query = query.include(query_resource, search_param, reverse=True)
    print(query.query_parameters)
    conditions = query.all()
    print(conditions)


def test_flatten_response(server):
    patients = server.query("Patient").limit(30)

    patients_df = flatten_response(patients)
    assert isinstance(patients_df, pd.DataFrame)
    assert len(patients_df) == 30


def test_flatten_resource(server):
    patient = server.query("Patient").limit(1).resources[0]
    flat_patient = flatten_resource(patient)
    print(flat_patient)

    condition = server.query("Condition").limit(1).resources[0]
    flat_condition = flatten_resource(condition)
    print(flat_condition)

    # observation = server.query("Observation").limit(1).resources[0]
    # flat_obs = flatten_resource(observation)


def test_resources_to_csv(server):
    patients = server.query("Patient").all().resources
    patients_df = flatten_resources(patients)
    patients_df.to_csv("patients.csv")

    if os.path.exists("patients.csv"):
        os.remove("patients.csv")

    conditions = server.query("Condition").all().resources
    conditions_df = flatten_resources(conditions)
    conditions_df.to_csv("conditions.csv")

    if os.path.exists("conditions.csv"):
        os.remove("conditions.csv")
