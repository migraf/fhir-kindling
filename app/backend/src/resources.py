from typing import List

from fhir.resources.fhirtypes import ReferenceType

from app.backend.models.resource import ResourceField
from fhir_kindling.util import get_resource_fields


def extract_query_fields(resource_name: str) -> List[ResourceField]:
    model_fields = get_resource_fields(resource_name)

    query_fields = []
    for field in model_fields:
        if field.type_ == ReferenceType:
            continue
        field = ResourceField(
            name=field.name,
            type=str(field.type_),
            description=field.field_info.description,
            title=field.field_info.title,
        )
        query_fields.append(field)

    return query_fields
