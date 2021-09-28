import json
from pathlib import Path
from typing import Union, List, Tuple
import pandas as pd

import requests
from requests.auth import AuthBase
from fhir.resources.domainresource import DomainResource
from fhir.resources.fhirtypes import DomainResourceType
from fhir.resources import FHIRAbstractModel

from fhir_kindling.fhir_server.auth import generate_auth, load_environment_auth_vars
from fhir_kindling.serde import flatten_bundle


# todo clean up authentication flow

def query_server(query_string: str = None,
                 resource: Union[FHIRAbstractModel, DomainResourceType, str] = None,
                 limit: int = 1000,
                 out_path: Union[str, Path] = None,
                 out_format: str = "json",
                 references: bool = False,
                 fhir_server_url: str = None, username: str = None, password: str = None, token: str = None,
                 fhir_server_type: str = None) -> Union[dict, Tuple[dict, list], pd.DataFrame]:
    """
    Execute a query against a server, either query all instances of a fhir resource or execute a given query string.
    Optionally store the results in a file either in csv format or as a raw fhir bundle json

    Args:
        query_string: Prebuilt query string to execute against the server's REST api
        resource: either string identifier of a resource
        limit: maximum number of resources to return, 0 returns all resources
        out_path: path under which to store the results
        out_format: format in which to store the results either csv or json
        references: whether to return a list of references to the resources
        fhir_server_url: url of the fhir server api endpoint
        username: username for basic auth
        password: password for basic auth
        token: token for bearer token auth
        fhir_server_type: type of the fhir server one of [hapi, blaze, ibm]

    Returns:
        dictionary containing the json response from the server, if references is True returns a tuple
        (bundle, references)
    """
    # Attempt to load environment authentication variables if nothing is given
    if not (username and password) and not token:
        username, password, token = load_environment_auth_vars()

    if query_string and resource:
        raise ValueError("Conflicting query information, both resource and query string are given.")

    # Create authentication and headers for the requests
    auth = generate_auth(username, password, token)
    headers = {"Content-Type": "application/fhir+json"}

    # If a resource type or identifier string is given query this resource or query by given url string
    if resource:
        response = query_resource(resource, fhir_server_url, auth, headers, limit=limit)

    elif query_string:
        response = query_with_string(query_string, fhir_server_url, auth, headers, limit=limit)

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

    if out_format == "df":
        df = flatten_bundle(bundle_json=response)
        return df

    if response and references:
        references = _extract_references_from_query_response(entries=response.get("entry"),
                                                             fhir_server_type=fhir_server_type)
        return response, references

    return response


def query_resource(resource: Union[DomainResource, DomainResourceType, str], fhir_server_url: str, auth: AuthBase,
                   headers: dict, fhir_server_type: str = None, count: int = 2000, limit: int = 0):
    """
    Query all instances up to limit from the server.

    Args:
        resource: Either string identifier of a resource or a FHIR resource type or instances
        fhir_server_url: api endpoint to execute the query against
        auth: authentication object for the request
        headers: headers to add to the request
        fhir_server_type: type of the fhir server
        count: maximum resources per page returned by the fhir server
        limit: maximum number of resources to return, all if 0

    Returns:
        bundle containing all instances of the resource on the server

    """
    if isinstance(resource, str):
        url = fhir_server_url + "/" + resource + "?"
    else:
        url = fhir_server_url + "/" + resource.get_resource_type() + "?"

    url += f"_count={limit if limit != 0 and limit < count else count}"
    response = _execute_query(url, auth, headers, limit)

    return response


def query_with_string(query_string: str, fhir_server_url: str, auth: AuthBase, headers: dict, count: int = 2000,
                      limit: int = None) -> dict:
    """
    Execute the given query string using the given fhir api endpoint and return the results

    Args:
        query_string: prebuilt query string to append to the api url and query
        fhir_server_url: api endpoint of the fhir server
        auth: authentication object for the fhir server
        headers: headers to add to the request
        count: maximum number of resources per page
        limit: maximum number of resources to return, all if 0

    Returns:
        bundle containing resources matching the query
    """
    # stitch together the query string with the api url
    if fhir_server_url[-1] == "/" and query_string[0] == "/":
        url = fhir_server_url[:-1] + query_string
    elif fhir_server_url[-1] != "/" and query_string[0] != "/":
        url = fhir_server_url + "/" + query_string
    else:
        url = fhir_server_url + query_string

    if "_count" not in query_string:
        # Set the count to the limit if limit is given
        if limit:
            limit_count = limit if count > limit != 0 else count
            url += f"&_count={limit_count}"
            response = _execute_query(url, auth, headers, limit)
        else:
            response = _execute_query(url, auth, headers, count)

    return response


def _execute_query(url: str, auth: AuthBase = None, headers: dict = None, limit: int = None) -> dict:
    r = requests.get(url=url, auth=auth, headers=headers)
    r.raise_for_status()

    response = r.json()
    # Query additional pages contained in the response and append all returned lists into a list of entries
    response = _resolve_response_pagination(response, auth, headers, limit)

    return response


def _resolve_response_pagination(response: dict, auth: AuthBase, headers: dict, limit: int = None) -> dict:
    entries = []
    entries.extend(response["entry"])

    if limit:
        if len(entries) >= limit:
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

    response["entry"] = entries[:limit] if limit else entries

    return response


def _extract_references_from_query_response(entries: List[dict], fhir_server_type: str):
    references = []
    if fhir_server_type == "hapi":
        for entry in entries:
            subject = entry.get("subject")
            if subject:
                references.append(subject["reference"])
            else:
                references.append(None)

    elif fhir_server_type in ["blaze", "ibm"]:
        for entry in entries:
            resource_reference = "/".join(entry["fullUrl"].split("/")[-2:])
            references.append(resource_reference)
    else:
        raise ValueError(f"Unsupported FHIR server: {fhir_server_type}")

    return references
