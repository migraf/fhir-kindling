from typing import Union, List
from pydantic.fields import ModelField

from fhir.resources.resource import Resource
from fhir.resources import get_fhir_model_class
from fhir.resources.fhirtypes import ResourceType


def get_resource_fields(resource: Union[Resource, ResourceType, str]) -> List[ModelField]:

    # If the resource is a string, then we need to get the resource class
    if isinstance(resource, str):
        resource = get_fhir_model_class(resource)

    # Get the resource model fields
    fields = list(resource.__fields__.values())
    return fields


