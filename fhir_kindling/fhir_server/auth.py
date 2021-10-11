import os

import click
import requests
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv, find_dotenv


def load_environment_auth_vars() -> tuple:
    """Attempts to load authentication information from environment variables if none is given, looks for a username
    under "FHIR_USER", password under "FHIR_PW" and the token under "FHIR_TOKEN"

    Returns:
        Tuple containing username, password and token if they were found or None if they are not present in the env vars

    """
    username = os.getenv("FHIR_USER", None)
    password = os.getenv("FHIR_PW", None)
    token = os.getenv("FHIR_TOKEN", None)

    return username, password, token


def generate_auth(username: str = None, password: str = None, token: str = None,
                  load_env: bool = False) -> requests.auth.AuthBase:
    """Generate authentication for the request to be sent to server. Either based on a given bearer token or using basic
    auth with username and password.

    Args:
      username: username for basic auth
      password: password for basic auth
      token: token to be used for bearer auth
      load_env: whether to attempt to load environment variables for auth

    Returns:
        requests auth object to use in an API call
    """
    if (not username and not password) and not token:

        if load_env:
            click.echo("No authentication given. Attempting authentication via environment variables")
            username, password, token = load_environment_auth_vars()

        if (not username and not password) and not token:
            raise ValueError("No authentication information given.")

    if (username and password) and token:
        raise ValueError("Conflicting authentication information both token and username:password set.")

    if username and not password:
        raise ValueError(f"Missing password for user: {username}")

    if username and password:
        return HTTPBasicAuth(username=username, password=password)
    # TODO request token from id provider if configured
    elif token:
        return BearerAuth(token=token)

    else:
        raise ValueError("No authentication information given")


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


if __name__ == '__main__':
    pass
