from typing import Optional, List, Any
from datetime import datetime

from sqlmodel import SQLModel

from app.backend.models.server import Server
from fhir_kindling.fhir_query import QueryResponse
from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters


class Query(SQLModel):
    server: Optional[Server] = None
    query_parameters: Optional[FHIRQueryParameters] = None
    query_string: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ResourceResults(SQLModel):
    resource: str
    items: List[Any]


class QueryResult(SQLModel):
    query: Query
    resources: List[ResourceResults]

    @classmethod
    def from_query_response(cls, query: Query, response: QueryResponse):
        resources = [
            ResourceResults(
                resource=response.resource,
                items=[r.dict(exclude_none=True) for r in response.resources],
            )
        ]
        for include in response.included_resources:
            resources.append(
                ResourceResults(
                    resource=include.resource_type,
                    items=[r.dict(exclude_none=True) for r in include.resources],
                )
            )
        return cls(query=query, resources=resources)
