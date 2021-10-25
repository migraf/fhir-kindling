import os
from typing import List, Union

import requests
from fhir.resources.bundle import BundleEntry, BundleEntryRequest

from fhir_kindling.fhir_server.auth import generate_auth
from fhir.resources import FHIRAbstractModel
from .query_functions import query_server
from .upload import generate_fhir_headers
from dotenv import load_dotenv, find_dotenv


def delete_resources(query: str = None, resource: Union[str, FHIRAbstractModel] = None, cascade: bool = False,
                     fhir_api_url: str = None, username: str = None, password: str = None, token: str = None,
                     fhir_server_type: str = "hapi"):
    pass


def delete_resource_by_type(resource: Union[str, FHIRAbstractModel],
                            fhir_api_url: str = None, username: str = None, password: str = None, token: str = None,
                            fhir_server_type: str = "hapi"
                            ):
    headers = generate_fhir_headers(fhir_server_type)
    auth = generate_auth(username, password, token)
    response, references = query_server(resource=resource, fhir_server_url=fhir_api_url, username=username, password=password,
                                        token=token, references=True, fhir_server_type=fhir_server_type)

    transaction = _make_delete_transaction(references)

    delete_response = requests.post(fhir_api_url, json=transaction, headers=headers, auth=auth)

    return delete_response


def _make_delete_transaction(urls: List[str]) -> dict:
    bundle_requests = []
    for url in urls:
        entry_request = BundleEntryRequest(
            **{
                "method": "DELETE",
                "url": url
            }
        )

        entry = BundleEntry(
            request=entry_request
        )
        bundle_requests.append(entry)

    bundle = {
        "type": "transaction",
        "resourceType": "Bundle",
        "entry": [entry.dict() for entry in bundle_requests]
    }
    return bundle


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    delete_resource_by_type(resource="MolecularSequence", fhir_api_url=os.getenv("IBM_API_URL"),
                            username=os.getenv("FHIR_USER"), password=os.getenv("FHIR_PW"), fhir_server_type="ibm")
