import os
from typing import Union
import requests
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.reference import Reference
from pathlib import Path
import json
from requests.auth import AuthBase

from fhir_kindling.auth import generate_auth
from pprint import pprint
from dotenv import load_dotenv, find_dotenv


def upload_bundle(bundle: Union[Bundle, Path, str],
                  fhir_api_url: str,
                  username: str = None,
                  password: str = None,
                  token: str = None,
                  auth_method: str = "basic",
                  fhir_server_type: str = "hapi",
                  references: bool = False):
    auth = generate_auth(username=username, password=password, token=token)

    if not isinstance(bundle, Bundle):
        bundle = _load_bundle(bundle)

    response = _upload_bundle(bundle, api_url=fhir_api_url, auth=auth, fhir_server_type=fhir_server_type, )
    if references:
        resource_references = _get_references_from_bundle_response(response)
        return response, resource_references
    else:
        return response


def upload_resource(resource,
                    fhir_api_url: str,
                    username: str = None,
                    password: str = None,
                    token: str = None,
                    auth_method: str = "basic",
                    fhir_server_type: str = "hapi",
                    reference: bool = True):
    auth = generate_auth(username=username, password=password, token=token)
    url = fhir_api_url + f"/{resource.resource_type}"

    r = requests.post(url=url, json=resource.dict(), headers=_generate_fhir_headers(fhir_server_type), auth=auth)
    print(r.text)

    if fhir_server_type == "ibm":
        if reference:
            location = r.headers["location"].split("/")
            print(location[-4:-2])
            resource_reference = Reference(
                **{"reference": f"{location[-4]}/{location[-3]}",
                   "type": location[-4]}
            )

            return r.headers, reference
        return r.headers
    else:

        r.raise_for_status()
        response = r.json()
        if reference:
            resource_reference = Reference(
                **{"reference": f"{response['resourceType']}/{response['id']}",
                   "type": response['resourceType']}
            )
            return response, resource_reference

        return response


def _get_references_from_bundle_response(response):
    references = []
    for entry in response["entry"]:
        location = entry["response"]["location"]
        reference = "/".join(location.split("/")[:2])

        references.append(reference)
    return references


def _load_bundle(bundle_path: Union[Path, str]) -> Bundle:
    with open(bundle_path, "r") as f:
        bundle_json = json.load(f)

    # todo dirty hack fix this
    for entry in bundle_json["entry"]:
        try:
            bundle_entry = BundleEntry(**entry)
        except Exception as e:
            entry["resource"]["code"] = entry["resource"]["category"][0]
            bundle_entry = BundleEntry(**entry)
    bundle = Bundle(**bundle_json)
    return bundle


def _parse_bundle(bundle):
    pass


def _cleanup_references(bundle):
    pass


def _upload_bundle(bundle: Bundle, api_url: str, auth: AuthBase, fhir_server_type: str):
    headers = _generate_fhir_headers(fhir_server_type)
    r = requests.post(api_url, auth=auth, data=bundle.json(), headers=headers)
    if fhir_server_type == "ibm":
        print(r.headers)
        return r.headers

    r.raise_for_status()

    return r.json()


def _generate_fhir_headers(fhir_server_type: str):
    headers = {}
    if fhir_server_type == "blaze":
        headers["Content-Type"] = "application/fhir+json"

    else:
        # todo figure out if other servers require custom headers for bundle upload
        headers["Content-Type"] = "application/fhir+json"

    return headers


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    bundle_path = "../examples/polar/bundles/POLAR_Testdaten_UKB.json"
    bundle = _load_bundle(bundle_path)
    print(bundle)
    # hapi upload
    response = upload_bundle(bundle=bundle, fhir_api_url=os.getenv("FHIR_API_URL"), username=os.getenv("FHIR_USER"),
                             password=os.getenv("FHIR_PW"), fhir_server_type=os.getenv("FHIR_SERVER_TYPE"))
    # blaze upload
    # response = upload_bundle(bundle=bundle, fhir_api_url=os.getenv("BLAZE_API_URL"), token=os.getenv("FHIR_TOKEN"),
    #                          fhir_server_type=os.getenv("FHIR_SERVER_TYPE"))
