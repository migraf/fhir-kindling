from typing import List

from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir_kindling.auth import generate_auth


def delete_resources(query: str = None, resource: str = None, cascade: bool = False,
                     fhir_api_url: str = None, username: str = None, password: str = None, token: str = None,
                     fhir_server_type: str = "hapi"):
    pass


def delete_resource_by_type():
    pass


def make_delete_transaction(urls: List[str]) -> Bundle:
    bundle_requests = []
    for url in urls:
        request = BundleEntryRequest(
            **{
                "method": "DELETE",
                "url": url
            }
        )
        bundle_requests.append(request)

    bundle = Bundle(
        **{
            "type": "transaction",
            "entry": bundle_requests
        }
    )

    return bundle
