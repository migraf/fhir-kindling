from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

# from fhir_kindling.fhir_server.fhir_server import FhirServer
import tqdm
from pydantic import BaseModel

from fhir_kindling.util.resources import valid_resource_name

if TYPE_CHECKING:
    from fhir_kindling.fhir_server import FhirServer


class ResourceSummary(BaseModel):
    resource: str
    count: int


class ServerSummary(BaseModel):
    name: Optional[str] = None
    resources: List[ResourceSummary]

    @property
    def available_resources(self) -> List[ResourceSummary]:
        return [r for r in self.resources if r.count > 0]


def create_server_summary(
    server: "FhirServer", resources: List[str], display: bool = True
) -> ServerSummary:
    """
    Create a summary of the server's resources and counts.
    Args:
        server: FhirServer object to summarize
        resources: list of resources to query/count
        display: whether to display a progress bar

    Returns:
        ServerSummary object containing a list of ResourceSummary objects
    """
    resource_summaries = []
    summary = {"name": server.api_address}

    pbar = tqdm.tqdm(resources, disable=not display)
    for resource in pbar:
        pbar.set_description(f"Querying {resource}")
        resource, valid = valid_resource_name(resource, strict=False)
        if not valid:
            continue
        count = server.query(resource).count()
        resource_summaries.append(ResourceSummary(resource=resource, count=count))
    summary["resources"] = resource_summaries
    return ServerSummary(**summary)


async def create_server_summary_async(
    server: "FhirServer", resources: List[str], display: bool = True
) -> ServerSummary:
    """
    Asynchronously create a summary of the server's resources and counts.

    Args:
        server: FhirServer object to summarize
        resources: list of resources to query/count
        display: whether to display a progress bar

    Returns:
        ServerSummary object containing a list of ResourceSummary objects
    """
    resource_summaries = []
    summary = {"name": server.api_address}

    pbar = tqdm.tqdm(resources, disable=not display)
    for resource in pbar:
        pbar.set_description(f"Querying {resource}")
        resource, valid = valid_resource_name(resource, strict=False)
        if not valid:
            continue
        count = await server.query_async(resource).count()
        resource_summaries.append(ResourceSummary(resource=resource, count=count))
    summary["resources"] = resource_summaries
    return ServerSummary(**summary)
