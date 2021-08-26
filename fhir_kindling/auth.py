import os

import click
import requests
from requests.auth import HTTPBasicAuth



def load_environment_auth_vars():
    """
    Attempts to load authentication information from environment variables if none is given

    :return:
    """
    username = os.getenv("FHIR_USER", None)
    password = os.getenv("FHIR_PW", None)
    token = os.getenv("FHIR_TOKEN", None)

    return username, password, token



def generate_auth(username, password, token) -> requests.auth.AuthBase:
    """
    Generate authoriation for the request to be sent to server. Either based on a given bearer token or using basic
    auth with username and password.

    :return: Auth object to pass to a requests call.
    """
    if (not username and not password) and not token:
        click.echo("No authentication given. Attempting authentication via environment variables")
        username = os.getenv("FHIR_USER", None)
        password = os.getenv("FHIR_PW", None)
        token = os.getenv("FHIR_TOKEN", None)

    if (username and password) and token:
        raise ValueError("Conflicting authentication information both token and username:password set.")

    if username and password:
        return HTTPBasicAuth(username=username, password=password)
    # TODO request token from id provider if configured
    elif token:
        return BearerAuth(token=token)

    else:
        raise ValueError("No authentication info given.")


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r
