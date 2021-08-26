import os
from typing import Union

import requests
from fhir.resources.domainresource import DomainResource
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient

from fhir_kindling.auth import generate_auth
from fhir_kindling.upload import _generate_fhir_headers
from dotenv import load_dotenv, find_dotenv


def query_resource(resource: Union[DomainResource, str],
                   fhir_server_url: str = None, username: str = None, password: str = None, token: str = None,
                   fhir_server_type: str = None):
    auth = generate_auth(username, password, token)

    if isinstance(resource, DomainResource):

        url = os.getenv("FHIR_API_URL") + "/" + resource.get_resource_type() + "?"

    else:
        url = os.getenv("FHIR_API_URL") + "/" + resource + "?"

    r = requests.get(url, auth=auth, headers=_generate_fhir_headers(fhir_server_type=fhir_server_type))


    print(r.text)


def resolve_relations():
    pass

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    query_resource(Observation.get_resource_type())
