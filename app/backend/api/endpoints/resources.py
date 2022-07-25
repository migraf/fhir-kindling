from typing import List

from fastapi import APIRouter

from fhir_kindling.util.resources import get_resource_fields
from fhir_kindling.generators.names import RESOURCE_NAMES

router = APIRouter()


@router.get("/", response_model=List[str])
def get_all_resource_names():
    return RESOURCE_NAMES
