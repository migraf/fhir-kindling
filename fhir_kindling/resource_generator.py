import pprint
from typing import List, Union

import requests
from fhir.resources.domainresource import DomainResource
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
import os
import pendulum
from requests.auth import HTTPBasicAuth


class FhirResourceGenerator:

    def __init__(self, n: int, resources: List[DomainResource] = None,
                 resource_type: DomainResource = None,
                 fhir_server: str = None, fhir_user: str = None, fhir_pw: str = None, fhir_token: str = None,
                 fhir_server_type: str = None):
        self.fhir_token = fhir_token if fhir_token else os.getenv("FHIR_TOKEN")
        self.fhir_pw = fhir_pw if fhir_pw else os.getenv("FHIR_PW")
        self.fhir_user = fhir_user if fhir_user else os.getenv("FHIR_USER")
        self.fhir_server = fhir_server if fhir_server else os.getenv("FHIR_SERVER_URL")
        self.fhir_server_type = fhir_server_type if fhir_server_type else os.getenv("FHIR_SERVER_TYPE")
        self.n = n
        self.resource_type = resource_type
        self.resources = resources

    def generate(self, upload: bool = False, out_dir: str = None):
        bundle = self.make_bundle()
        if upload:
            self.upload_resource_or_bundle(bundle=bundle)

        if out_dir:
            path = os.path.join(out_dir, f"bundle-{pendulum.now().isoformat()}.json")
            with open(path, "w") as bundle_file:
                bundle_file.write(bundle.json())

    def make_bundle(self) -> Bundle:
        entries = self._generate_bundle_entries()
        bundle_data = {
            "type": "transaction",
            "entry": entries
        }
        bundle = Bundle(**bundle_data)
        return bundle

    def _generate_bundle_entries(self):
        entries = []
        for resource in self.resources:
            bundle_entry_dict = {
                "resource": resource,
                "request": BundleEntryRequest(**{"method": "POST", "url": self.resource_type.get_resource_type()})
            }
            entry = BundleEntry(**bundle_entry_dict)
            entries.append(entry)
        return entries

    def upload_resource_or_bundle(self, resource=None, bundle: Bundle = None):
        auth = self._generate_auth()
        api_url = self._generate_api_url()
        if bundle:
            self._upload_bundle(bundle=bundle, api_url=api_url, auth=auth)
        if resource:
            # TODO upload single resource
            pass

    def _generate_api_url(self) -> str:
        url = self.fhir_server
        if self.fhir_server_type == "ibm":
            url += "/fhir-server/api/v4"

        elif self.fhir_server_type in ["blaze", "hapi"]:
            url += "/fhir"

        else:
            raise ValueError(f"Unsupported FHIR server type: {self.fhir_server_type}")

        return url

    def _upload_bundle(self, bundle: Bundle, api_url: str, auth: requests.auth.AuthBase):
        headers = self._generate_bundle_headers()
        r = requests.post(api_url, auth=auth, data=bundle.json(), headers=headers)
        r.raise_for_status()

    def _generate_bundle_headers(self):
        headers = {}
        if self.fhir_server_type == "blaze":
            headers["Content-Type"] = "application/fhir+json"

        else:
            # todo figure out if other servers require custom headers for bundle upload
            headers["Content-Type"] = "application/fhir+json"

        return headers

    def display_schema(self):
        pprint.pprint(self.resource_type.schema())

    def _generate_auth(self) -> requests.auth.AuthBase:
        """
        Generate authoriation for the request to be sent to server. Either based on a given bearer token or using basic
        auth with username and password.

        :return: Auth object to pass to a requests call.
        """
        if self.fhir_user and self.fhir_pw:
            return HTTPBasicAuth(username=self.fhir_user, password=self.fhir_pw)
        # TODO request token from id provider if configured
        elif self.fhir_token:
            return BearerAuth(token=self.fhir_token)


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r
