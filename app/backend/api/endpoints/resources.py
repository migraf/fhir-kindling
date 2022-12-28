from typing import List

from fastapi import APIRouter, HTTPException

from app.backend.models.resource import ResourceFields
from app.backend.src.resources import extract_query_fields
from fhir_kindling.util.resources import valid_resource_name
from fhir_kindling.generators.names import RESOURCE_NAMES


router = APIRouter()


@router.get("/", response_model=List[str])
def get_all_resource_names():
    return RESOURCE_NAMES


@router.get("/{resource_name}/fields", response_model=ResourceFields)
def get_resource_fields(resource_name: str):
    try:
        valid_resource_name(resource_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])

    fields = ResourceFields(
        resource=resource_name, fields=extract_query_fields(resource_name)
    )
    return fields
