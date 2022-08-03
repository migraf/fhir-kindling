from typing import Optional, List
from sqlmodel import SQLModel

from app.backend.models.server import Server
from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters


class Query(SQLModel):
    server: Optional[Server] = None
    query_parameters: Optional[FHIRQueryParameters] = None
    query_string: Optional[str] = None

