import json

import pytest
import requests
from fhir.resources.patient import Patient
from requests.auth import HTTPBasicAuth
import os
from unittest import mock

# from fhir_kindling.fhir_query import query_server, query_resource, query_with_string
# from fhir.resources.procedure import Procedure
# from fhir_kindling.upload import generate_fhir_headers
# from fhir_kindling.fhir_server.auth import generate_auth
# import pandas as pd
#
#
# @pytest.fixture
# def api_url():
#     """
#     Base api url
#
#     """
#     return "http://hapi.fhir.org/baseR4"
#
#
# @pytest.fixture
# def bogus_auth():
#     """
#     Lower level functions expect auth information to be given. The public test server does not require but it needs to
#     be present.
#     Returns:
#
#     """
#
#     return HTTPBasicAuth(username="bogus", password="auth")
#
#
# @pytest.fixture
# def fhir_headers():
#     return generate_fhir_headers(fhir_server_type="hapi")
#
#
# def test_api_connection(api_url):
#     url = api_url + "/metadata"
#     r = requests.get(url)
#
#     r.raise_for_status()
#     assert r.text
#
#
# def test_query_resource(api_url, bogus_auth, fhir_headers):
#     limit = 100
#     response = query_resource("Patient", fhir_server_url=api_url, auth=bogus_auth, headers=fhir_headers, limit=limit)
#     assert response
#     assert len(response["entry"]) == limit
#
#     token_auth = generate_auth(token="test_token")
#     response2 = query_resource(Patient, fhir_server_url=api_url, auth=token_auth, headers=fhir_headers, limit=limit)
#     assert response == response2
#
#     # test paginated responses
#     response3 = query_resource("Patient", fhir_server_url=api_url, auth=bogus_auth, headers=fhir_headers, limit=2500)
#     assert len(response3["entry"]) == 2500
#
#
# def test_query_with_string(api_url, bogus_auth, fhir_headers):
#     # simple query for patients by age
#     query_string_1 = "Patient?birthdate=gt1990"
#
#     response_1 = query_with_string(query_string_1, api_url, bogus_auth, fhir_headers, limit=100)
#
#     assert response_1
#     assert len(response_1["entry"]) == 100
#
#     # test that / mismatch is resolved
#     query_string_2 = "/Observation?patient.birthdate=gt1990"
#     response_2 = query_with_string(query_string_2, api_url + "/", bogus_auth, fhir_headers, limit=100)
#
#     assert response_2
#
#
# def test_query(api_url, fhir_headers):
#     query_string = "/Observation?patient.birthdate=gt1990"
#
#     response = query_server(query_string=query_string, limit=100, username="test", password="password",
#                             fhir_server_url=api_url, fhir_server_type="hapi", references=False)
#
#     assert response
#
#     response = query_server(resource="Observation", limit=100, username="test", password="password",
#                             fhir_server_url=api_url, fhir_server_type="hapi", references=False)
#
#     assert response
#
#     with pytest.raises(ValueError):
#         response = query_server(limit=100, username="test", password="password", fhir_server_url=api_url,
#                                 fhir_server_type="hapi", references=False)
#
#     with pytest.raises(ValueError):
#         response = query_server(query_string=query_string, limit=100,
#                                 fhir_server_url=api_url, fhir_server_type="hapi", references=False)
#     with pytest.raises(ValueError):
#         response = query_server(query_string=query_string, limit=100, username="test", password="pw", token="hello",
#                                 fhir_server_url=api_url, fhir_server_type="hapi", references=False)
#
#
# @mock.patch.dict(os.environ, {"FHIR_USER": "test", "FHIR_PW": "password"})
# def test_query_with_env(api_url, fhir_headers):
#     query_string = "/Observation?patient.birthdate=gt1990"
#     response = query_server(query_string=query_string, limit=100, fhir_server_url=api_url, fhir_server_type="hapi",
#                             references=False)
#     assert response
#
#
# def test_query_output(api_url, tmp_path):
#     query_string = "/Observation?patient.birthdate=gt1990"
#
#     json_path = tmp_path / "query_results.json"
#     csv_path = tmp_path / "query_results.csv"
#
#     response = query_server(query_string=query_string, limit=100, fhir_server_url=api_url, fhir_server_type="hapi",
#                             token="hello",
#                             out_path=json_path, out_format="json", references=False)
#
#     loaded_response = json.loads(json_path.read_bytes())
#
#     assert loaded_response
#     assert len(loaded_response["entry"]) == len(response["entry"])
#
#     # test serialization to csv
#     response = query_server(query_string=query_string, limit=100, fhir_server_url=api_url, fhir_server_type="hapi",
#                             token="hello",
#                             out_path=csv_path, out_format="csv", references=False)
#
#     df = pd.read_csv(csv_path)
#
#     assert len(df) == len(response["entry"])
#
#     with pytest.raises(NotImplementedError):
#         response = query_server(query_string=query_string, limit=100, fhir_server_url=api_url, fhir_server_type="hapi",
#                                 token="hello",
#                                 out_path=csv_path, out_format="hdf", references=False)
#
#
# def test_query_references(api_url):
#     query_string = "/Observation?patient.birthdate=gt1990"
#
#     response, references = query_server(query_string=query_string, limit=100, fhir_server_url=api_url, fhir_server_type="hapi",
#                                         token="hello", references=True)
#
#     assert len(response["entry"]) == len(references)
