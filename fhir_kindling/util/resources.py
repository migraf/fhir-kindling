from typing import Union, List

from fhir.resources.bundle import BundleEntry, BundleEntryRequest
from fhir.resources.fhirresourcemodel import FHIRResourceModel
from pydantic.fields import ModelField

from fhir.resources.resource import Resource
from fhir.resources import get_fhir_model_class
from fhir.resources.fhirtypes import ResourceType


def get_resource_fields(resource: Union[Resource, ResourceType, str]) -> List[ModelField]:
    """
    Get the fields of a resource.
    Args:
        resource:

    Returns:

    """
    # If the resource is a string, then we need to get the resource class
    if isinstance(resource, str):
        resource = get_fhir_model_class(resource)

    # Get the resource model fields
    fields = list(resource.__fields__.values())
    return fields


def valid_resource_name(resource_name: str) -> str:
    """

    Args:
        resource_name:

    Returns:

    """
    try:
        get_fhir_model_class(resource_name)
    except KeyError:
        raise ValueError(f"Invalid resource name: {resource_name}")
    return resource_name


def generate_bundle_entry(resource: Union[Resource, FHIRResourceModel, dict], method: str = "POST") -> BundleEntry:
    if isinstance(resource, dict):
        url = resource.get("resourceType")
        id = resource.get("id")
    else:
        url = resource.resource_type
        id = resource.id

    # Post a resource to the base endpoint
    if method.lower() == "post":
        pass
    elif method.lower() == "put":
        url += f"/{id}"

    return BundleEntry(
        request=BundleEntryRequest(
            url=url if url else f"url/{resource.get('id')}",
            method=method
        ),
        resource=resource
    )

