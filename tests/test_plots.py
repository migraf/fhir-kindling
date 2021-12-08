import os
import pytest
from dotenv import load_dotenv, find_dotenv

from fhir_kindling import FhirServer

from fhir_kindling.plots import server_summary_plot, resource_summary_plot, plot_resource_field
from tests.fixtures import fhir_server

fhir_server = fhir_server


@pytest.fixture
def api_url():
    """
    Base api url and env vars
    """
    load_dotenv(find_dotenv())

    return os.getenv("FHIR_API_URL", "http://test.fhir.org/r4")


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


def test_server_summary(fhir_server):
    summary = fhir_server.summary()

    plot_dict = server_summary_plot(summary)
    print(plot_dict)


def test_resource_summary_basic(fhir_server):
    patients = fhir_server.query("Patient")
    assert patients
    summary_plot = resource_summary_plot(patients, ["gender"])
    assert summary_plot


def test_plot_resource_field(fhir_server):
    patients = fhir_server.query("Patient").all()
    plot_resource_field(patients.resources, field="gender")
