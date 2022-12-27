from typing import Union, List, Type

from pydantic.fields import ModelField

from fhir.resources.resource import Resource
from fhir.resources import get_fhir_model_class, FHIRAbstractModel
from fhir.resources.fhirtypes import ResourceType


def get_resource_fields(
    resource: Union[Resource, ResourceType, str, Type[FHIRAbstractModel]]
) -> List[ModelField]:
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
    Checks if the given resource name is a valid FHIR resource name.
    Args:
        resource_name:

    Returns:

    """
    try:
        get_fhir_model_class(resource_name)
    except KeyError:
        raise ValueError(f"Invalid resource name: {resource_name}")
    return resource_name


def check_resource_contains_field(
    resource: Union[Resource, ResourceType, str, Type[FHIRAbstractModel]],
    field_name: str,
):
    """
    Checks if the given resource contains the given field.
    Args:
        resource: Name of the resource to check.
        field_name: field name to check for.

    Returns:

    Raises:
        ValueError: If the resource does not contain the field.

    """

    fields = get_resource_fields(resource)
    field_names = [field.name for field in fields]
    if field_name not in field_names:
        raise ValueError(f"Resource {resource} does not contain field {field_name}")
