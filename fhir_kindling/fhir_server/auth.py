import datetime
import os
from typing import Tuple, Union

import httpx


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


class OIDCAuth:
    expires_at: Union[datetime.datetime, None]
    access_token: Union[str, None]
    refresh_token: Union[str, None]
    token_type: Union[str, None]
    client_id: str
    client_secret: str
    oidc_provider_url: str

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        oidc_provider_url: str,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.oidc_provider_url = oidc_provider_url
        self.expires_at = None

    def get_token(self):
        if self.is_expired() or not self.access_token:
            self.refresh()
        return self.access_token

    def refresh(self):
        response = httpx.post(
            self.oidc_provider_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        response.raise_for_status()
        self._parse_response_dict(response.json())

    def _parse_response_dict(self, response_dict: dict):
        self.expires_at = datetime.datetime.now() + datetime.timedelta(
            seconds=response_dict["expires_in"]
        )
        self.access_token = response_dict["access_token"]
        self.refresh_token = response_dict.get("refresh_token", None)
        self.token_type = response_dict["token_type"]

    def is_expired(self) -> bool:
        if not self.expires_at:
            return True
        return datetime.datetime.now() > self.expires_at


def generate_auth(
    username: str = None,
    password: str = None,
    token: str = None,
    load_env: bool = False,
) -> httpx.Auth:
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
            print(
                "No authentication given. Attempting authentication via environment variables"
            )
            username, password, token = load_environment_auth_vars()

        if (not username and not password) and not token:
            raise ValueError("No authentication information given.")

    if (username and password) and token:
        raise ValueError(
            "Conflicting authentication information both token and username:password set."
        )

    if username and not password:
        raise ValueError(f"Missing password for user: {username}")

    if username and password:
        return httpx.BasicAuth(username=username, password=password)
    elif token:
        return BearerAuth(token=token)

    else:
        raise ValueError("No authentication information given")


def get_oidc_token(
    client_id: str, client_secret: str, oidc_provider_url: str, old_token: dict
) -> dict:
    """Get a new token from the OIDC provider using the refresh token from the old token

    Args:
        client_id: client id for the OIDC provider
        client_secret: client secret for the OIDC provider
        oidc_provider_url: url for the OIDC provider
        old_token: old token to be refreshed

    Returns:
        new token from the OIDC provider
    """

    refresh_token = old_token["refresh_token"]
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = httpx.post(oidc_provider_url, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Could not get new token")


def auth_info_from_env() -> Union[str, Tuple[str, str], Tuple[str, str, str]]:
    # First try to load basic auth information
    username = os.getenv("FHIR_USER")
    # Static token auth
    token = os.getenv("FHIR_TOKEN")
    # oauth2/oidc authentication
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    oidc_provider_url = os.getenv("OIDC_PROVIDER_URL")

    if username and token:
        raise EnvironmentError(
            "Conflicting auth information, bother username and token present."
        )
    if username and client_id:
        raise EnvironmentError(
            "Conflicting auth information, bother username and client id present"
        )
    if token and client_id:
        raise EnvironmentError(
            "Conflicting auth information, bother static token and client id present"
        )

    if username:
        password = os.getenv("FHIR_PW")
        if not password:
            raise EnvironmentError(f"No password specified for user: {username}")
        else:
            return username, password
    if token:
        return token

    if client_id and not client_secret:
        raise EnvironmentError(
            "Insufficient auth information, client id specified but no client secret found."
        )

    if (client_id and client_secret) and not oidc_provider_url:
        raise EnvironmentError(
            "Insufficient auth information, client id and secret "
            "specified but no provider URL found"
        )
    if client_id and client_secret and oidc_provider_url:
        return client_id, client_secret, oidc_provider_url


class BearerAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request
