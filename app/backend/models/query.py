from typing import Optional, List
from sqlmodel import SQLModel
from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters


class Query(SQLModel):
    server: Optional