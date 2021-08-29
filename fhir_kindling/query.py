import json
import os
from pathlib import Path
from typing import Union, List, Tuple

import requests
from requests.auth import AuthBase, HTTPBasicAuth
from fhir.resources.domainresource import DomainResource
from fhir.resources.fhirtypes import DomainResourceType

from fhir_kindling.auth import generate_auth, load_environment_auth_vars
from fhir_kindling.serde import flatten_bundle
from fhir_kindling.upload import generate_fhir_headers
from dotenv import load_dotenv, find_dotenv


# todo clean up authentication flow

def query(query_string: str = None,
          resource: Union[DomainResource, DomainResourceType, str] = None,
          out_path: Union[str, Path] = None,
          out_format: str = "json",
          references: bool = True,
          fhir_server_url: str = None, username: str = None, password: str = None, token: str = None,
          fhir_server_type: str = None) -> Union[List[dict], Tuple[List[dict], List[str]]]:
    # Attempt to load environment authentication variables if nothing is given
    if not (username and password) and not token:
        username, password, token = load_environment_auth_vars()

    if query_string and resource:
        raise ValueError("Conflicting query information, both resource and query string are given.")

    # Create authentication and headers for the requests
    auth = generate_auth(username, password, token)
    headers = generate_fhir_headers(fhir_server_type)

    # If a resource type or identifier string is given query this resource
    if resource:
        response = query_resource(resource, fhir_server_url, auth, headers)

    elif query_string:
        response = query_with_string(query_string, fhir_server_url, auth, headers)

    else:
        raise ValueError("No query information given.")

    if out_path:
        if out_format == "json":
            with open(out_path, "w") as out_file:
                json.dump(response, out_file)
        elif out_format == "csv":
            df = flatten_bundle(bundle_json=response)
            df.to_csv(out_path)
        else:
            raise NotImplementedError("Only csv and json currently supported.")

    # todo fix reference parsing
    if response and references:
        references = _extract_references_from_query_response(entries=response.get("entry"),
                                                             fhir_server_type=fhir_server_type)

        return response, references

    return response


def query_resource(resource: Union[DomainResource, DomainResourceType, str], fhir_server_url: str, auth: AuthBase,
                   headers: dict, fhir_server_type: str = None, count: int = 2000, limit: int = 0):
    if isinstance(resource, str):
        url = fhir_server_url + "/" + resource + "?"
    else:
        url = fhir_server_url + "/" + resource.get_resource_type() + "?"

    url += f"_count={limit if limit != 0 and limit < count else count}"
    response = _execute_query(url, auth, headers, limit)

    return response


def query_with_string(query_string: str, fhir_server_url: str, auth: AuthBase, headers: dict, count: int = 2000,
                      limit: int = 0):
    # stitch together the query string with the api url
    if fhir_server_url[-1] == "/" and query_string[0] == "/":
        url = fhir_server_url[:-1] + query_string
    elif fhir_server_url[-1] != "/" and query_string[0] != "/":
        url = fhir_server_url + "/" + query_string
    else:
        url = fhir_server_url + query_string

    if "_count" not in query_string:
        # Set the count to the limit if limit is given
        limit_count = limit if count > limit != 0 else count
        url += f"&_count={limit_count}"

    reponse = _execute_query(url, auth, headers, limit)

    return reponse


def _execute_query(url: str, auth: AuthBase = None, headers: dict = None, limit: int = 0) -> List[dict]:
    r = requests.get(url=url, auth=auth, headers=headers)
    r.raise_for_status()
    response = r.json()
    # Query additional pages contained in the response and append all returned lists into a list of entries
    response = _resolve_response_pagination(response, auth, headers, limit)

    return response


def _resolve_response_pagination(response: dict, auth: AuthBase, headers: dict, limit: int):
    entries = []
    entries.extend(response["entry"])
    if len(entries) >= limit != 0:
        return response

    while response.get("link", None):

        if limit != 0 and len(entries) >= limit:
            print("Limit reached stopping pagination resolve")
            break

        next_page = next((link for link in response["link"] if link.get("relation", None) == "next"), None)
        if next_page:
            response = requests.get(next_page["url"], auth=auth, headers=headers).json()
            entries.extend(response["entry"])
        else:
            break

    response["entry"] = entries[:limit]

    return response


def _extract_references_from_query_response(entries: List[dict], fhir_server_type: str):
    references = []
    if fhir_server_type == "hapi":
        pass

    elif fhir_server_type == "blaze":
        for entry in entries:
            resource_reference = "/".join(entry["fullUrl"].split("/")[-2:])
            references.append(resource_reference)
    elif fhir_server_type == "ibm":
        pass
    else:
        raise ValueError(f"Unsupported FHIR server: {fhir_server_type}")

    return references


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    # response = query(
    #     # query_string="/MolecularSequence?patient.organization.name=DEMO_HIV&_format=json&_limit=1000",
    #     resource="Observation",
    #     fhir_server_url=os.getenv("BLAZE_API_URL"),
    #     out_path="test.csv",
    #     out_format="csv",
    #     token=os.getenv("FHIR_TOKEN"), fhir_server_type="blaze", references=False)

    response = query_resource("Procedure", fhir_server_url="http://hapi.fhir.org/baseR4",
                              auth=HTTPBasicAuth(username="bogus", password="auth"),
                              headers=generate_fhir_headers("hapi"), limit=100)
    print(response)
