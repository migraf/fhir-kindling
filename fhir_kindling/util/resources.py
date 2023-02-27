from typing import List, Tuple, Type, Union

from fhir.resources import FHIRAbstractModel, get_fhir_model_class
from fhir.resources.fhirtypes import ResourceType
from fhir.resources.resource import Resource
from pydantic.fields import ModelField


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


def valid_resource_name(
    resource_name: str, strict: bool = True
) -> Union[str, Tuple[str, bool]]:
    """
    Checks if the given resource name is a valid FHIR resource name.
    Args:
        resource_name:

    Returns:

    """
    try:
        get_fhir_model_class(resource_name)
        if strict:
            return resource_name
        return resource_name, True
    except KeyError:
        if strict:
            raise ValueError(f"Invalid resource name: {resource_name}")
        return resource_name, False


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
