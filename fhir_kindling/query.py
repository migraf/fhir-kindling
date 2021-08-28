import os
from pathlib import Path
from typing import Union, List, Tuple

import requests
from requests.auth import AuthBase
from fhir.resources.domainresource import DomainResource
from fhir.resources.fhirtypes import DomainResourceType

from fhir_kindling.auth import generate_auth, load_environment_auth_vars
from fhir_kindling.upload import _generate_fhir_headers
from dotenv import load_dotenv, find_dotenv


# todo clean up authentication flow

def query(query_string: str = None,
          resource: Union[DomainResource, DomainResourceType, str] = None,
          out_path: Union[str, Path] = None,
          out_format: Union[str, Path] = None,
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
    headers = _generate_fhir_headers(fhir_server_type)

    # If a resource type or identifier string is given query this resource
    if resource:
        response = query_resource(resource, fhir_server_url, auth, headers)

    elif query_string:
        response = query_with_string(query_string, fhir_server_url, auth, headers)

    else:
        raise ValueError("No query information given.")
    # todo fix reference parsing
    if response and references:
        references = _extract_references_from_query_response(entries=response.get("entry"),
                                                             fhir_server_type=fhir_server_type)

        return response, references

    return response


def query_resource(resource: Union[DomainResource, str], fhir_server_url: str, auth: AuthBase, headers: dict,
                   fhir_server_type: str = None):
    if isinstance(resource, DomainResource):
        url = fhir_server_url + "/" + resource.get_resource_type() + "?"
    else:
        url = fhir_server_url + "/" + resource + "?"
    response = _execute_query(url, auth, headers)

    return response


def query_with_string(query_string: str, fhir_server_url: str, auth: AuthBase, headers: dict):
    # stitch together the query string with the api url
    if fhir_server_url[-1] == "/" and query_string[0] == "/":
        url = fhir_server_url[:-1] + query_string
    elif fhir_server_url[-1] != "/" and query_string[0] != "/":
        url = fhir_server_url + "/" + query_string
    else:
        url = fhir_server_url + query_string

    reponse = _execute_query(url, auth, headers)

    return reponse


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


def _execute_query(url: str, auth: AuthBase = None, headers: dict = None) -> List[dict]:
    r = requests.get(url=url, auth=auth, headers=headers)
    r.raise_for_status()
    response = r.json()
    # Query additional pages contained in the response and append all returned lists into a list of entries
    response = _resolve_response_pagination(response, auth, headers)

    return response


def _resolve_response_pagination(response, auth, headers):
    entries = []
    entries.append(response["entry"])
    while response.get("link", None):
        next_page = next((link for link in response["link"] if link.get("relation", None) == "next"), None)
        if next_page:
            response = requests.get(next_page["url"], auth=auth, headers=headers).json()
            entries.extend(response["entry"])
        else:
            break
    else:
        entries = response["entry"]

    response["entry"] = entries

    return response


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    response = query(
        query_string="/MolecularSequence?patient.organization.name=DEMO_HIV&_format=json&_limit=1000",
        fhir_server_url=os.getenv("FHIR_API_URL"),
        token=os.getenv("FHIR_TOKEN"), fhir_server_type="blaze", references=False)

    print(response)
    print(len(response["entry"]))
