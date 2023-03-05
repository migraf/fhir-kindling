from enum import Enum
from typing import List, Union

from fhir.resources import FHIRAbstractModel, construct_fhir_element
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource


class TransactionMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class TransactionType(str, Enum):
    TRANSACTION = "transaction"
    BATCH = "batch"


def make_transaction_bundle(
    transaction_type: TransactionType = TransactionType.TRANSACTION,
    method: Union[TransactionMethod, str] = TransactionMethod.POST,
    resources: Union[List[Resource], List[dict]] = None,
    references: Union[List[Reference], List[str]] = None,
) -> Bundle:
    """
    Create a transaction bundle based on the resources, references, transaction type, and method.
    Args:
        transaction_type:
        method:
        resources:
        references:

    Returns:

    """

    # validate input parameters
    _validate_transaction_input(method, references, resources)

    bundle = Bundle.construct()
    bundle.type = transaction_type.value
    if resources:
        if not (
            isinstance(resources[0], FHIRAbstractModel)
            or isinstance(resources[0], dict)
        ):
            raise ValueError(
                "Resources must be a list of FHIR resources or a list of dicts"
            )
        entries = [
            make_transaction_entry(method, resource=resource) for resource in resources
        ]

    else:
        entries = []
        for reference in references:
            if isinstance(reference, Reference):
                reference = reference.reference
            entries.append(make_transaction_entry(method, url=reference))

    bundle.entry = entries

    return Bundle(**bundle.dict(exclude_none=True))


def _validate_transaction_input(
    method: Union[TransactionMethod, str],
    references: Union[List[Reference], List[str]],
    resources: Union[List[Resource], List[dict]],
):
    if isinstance(method, str):
        method = TransactionMethod(method)
    if not resources and not references:
        raise ValueError("Either resources or references must be provided")
    if resources and references:
        raise ValueError("Only one of resources or references can be provided")
    if method in [TransactionMethod.POST, TransactionMethod.PUT]:
        # if method is POST or PUT, resources must be provided
        if not resources:
            raise ValueError("Resources must be provided for POST and PUT transactions")

    elif method == TransactionMethod.GET:
        if not references:
            raise ValueError("References must be provided for GET transactions")


def make_transaction_entry(
    method: Union[TransactionMethod, str],
    url: str = None,
    resource: Union[Resource, dict] = None,
) -> BundleEntry:
    """Create a transaction entry for a bundle based on the method, url, and resource.
    If only a resource is provided, the url will be constructed from the resource otherwise the given url will be used.

    Args:
        method: the method to use for the transaction one of GET, POST, PUT, DELETE
        url: optional relative url to use for the transaction
        resource: optional FHIR resource to use for the transaction

    Returns:
        The transaction entry
    """
    if isinstance(method, str):
        method = TransactionMethod(method)

    if not url and not resource:
        raise ValueError("Either url or resource must be provided.")

    entry = BundleEntry.construct()

    if resource:
        # construct the fhir element if the resource is a dict
        if isinstance(resource, dict):
            try:
                resource = construct_fhir_element(
                    resource.get("resourceType"), resource
                )
            except Exception as e:
                raise ValueError(
                    f"Unable to construct resource from dict: {resource} \n{e}"
                )
        # remove the id if the method is POST (create)
        if method == TransactionMethod.PUT and not resource.id:
            raise ValueError("PUT requires a resource with an id")
        if method == TransactionMethod.POST:
            if resource.id:
                del resource.id
        _add_resource_to_entry(entry, resource)

    url = _get_transaction_url_for_method(method, url, resource)

    entry.request = BundleEntryRequest(**{"method": method.value, "url": url})

    return entry


def _get_transaction_url_for_method(
    method: TransactionMethod, url: str = None, resource: Resource = None
) -> str:
    """
    Get the url for a transaction entry based on the method, url, and resource.
    Args:
        method:
        url:
        resource:

    Returns:

    """
    if method == TransactionMethod.GET:
        if not url:
            url = resource.relative_path()
    elif method == TransactionMethod.PUT:
        if not resource:
            raise ValueError("PUT requires a resource")
        url = resource.relative_path()

    elif method == TransactionMethod.DELETE:
        if not url:
            url = resource.relative_path()
    else:
        if not url:
            url = resource.get_resource_type()

    return url


def _add_resource_to_entry(
    entry: BundleEntry, resource: Union[FHIRAbstractModel, dict]
):
    if isinstance(resource, FHIRAbstractModel):
        entry.resource = resource
    elif isinstance(resource, dict):
        entry.resource = construct_fhir_element(resource.get("resourceType"), resource)
    else:
        raise ValueError("Resource must be a FHIR resource or a dict")
