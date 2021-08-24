from typing import Union

import requests
from fhir.resources.bundle import Bundle
from pathlib import Path
import json

from requests.auth import HTTPBasicAuth


def upload_bundle(bundle: Union[Bundle, Path, str],
                  fhir_api_url: str,
                  username: str = None,
                  password: str = None,
                  token: str = None,
                  auth_method: str = "basic",
                  fhir_server_type: str = "hapi"):
    auth = _generate_auth(username=username, password=password, token=token)

    if not isinstance(bundle, Bundle):
        bundle = _load_bundle(bundle)

    response = _upload_bundle(bundle, api_url=fhir_api_url, auth=auth, fhir_server_type=fhir_server_type)
    print(response)


def _load_bundle(bundle_path: Union[Path, str]) -> Bundle:
    with open(bundle_path, "r") as f:
        bundle_json = json.load(f)

    bundle = Bundle(**bundle_json)
    return bundle


def _upload_bundle(bundle: Bundle, api_url: str, auth: requests.auth.AuthBase, fhir_server_type: str):
    headers = _generate_bundle_headers(fhir_server_type)
    r = requests.post(api_url, auth=auth, data=bundle.json(), headers=headers)
    print(r.text)
    r.raise_for_status()
    return r.json()


def _generate_bundle_headers(fhir_server_type: str):
    headers = {}
    if fhir_server_type == "blaze":
        headers["Content-Type"] = "application/fhir+json"

    else:
        # todo figure out if other servers require custom headers for bundle upload
        headers["Content-Type"] = "application/fhir+json"

    return headers


def _generate_auth(username, password, token) -> requests.auth.AuthBase:
    """
    Generate authoriation for the request to be sent to server. Either based on a given bearer token or using basic
    auth with username and password.

    :return: Auth object to pass to a requests call.
    """

    if username and password:
        return HTTPBasicAuth(username=username, password=password)
    # TODO request token from id provider if configured
    elif token:
        return BearerAuth(token=token)


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r
