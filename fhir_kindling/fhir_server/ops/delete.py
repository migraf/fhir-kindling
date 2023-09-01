from typing import TYPE_CHECKING, List, Union

from fhir.resources import FHIRAbstractModel
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource

from fhir_kindling.fhir_query import FhirQueryAsync, FhirQuerySync
from fhir_kindling.fhir_server.server_responses import DeleteResponse
from fhir_kindling.fhir_server.transactions import (
    TransactionMethod,
    make_transaction_bundle,
)
from fhir_kindling.serde.json import json_dict
from fhir_kindling.util.references import reference_graph, resource_from_graph_node

if TYPE_CHECKING:
    from fhir_kindling import FhirServer


def delete(
    server: "FhirServer",
    resources: List[Union[Resource, FHIRAbstractModel]] = None,
    references: List[Union[str, Reference]] = None,
    query: FhirQuerySync = None,
) -> DeleteResponse:
    """Delete resources from the server while respecting referential integrity. This means that resources are deleted
    in reverse order of their dependencies, so that resources that depend on other resources are deleted before the
    resources they depend on.

    Args:
        server: The server to delete the resources from.
        resources: A list of resources to delete with ids assigned from server
        references: List of references to delete. Defaults to None.
        query: Query specifying the resources to delete. Defaults to None.
    """
    _validate_delete_args(resources, references, query)

    if query:
        delete_resources = query.all().resources

    elif references:
        delete_resources = server.get_many(references)
    else:
        delete_resources = resources

    delete_response = DeleteResponse(
        server=server.api_address,
        resource_ids=[],
    )

    if len(delete_resources) == 0:
        return delete_response

    if len(delete_resources) == 1:
        delete_bundle = make_transaction_bundle(
            method=TransactionMethod.DELETE,
            resources=delete_resources,
        )
        with server._sync_client() as client:
            server_response = client.post(
                server.api_address,
                json=json_dict(delete_bundle),
            )
            server_response.raise_for_status()
            delete_response.add_resource_ids(delete_resources)
        return delete_response

    for resource_batch in _resolve_delete_graph(delete_resources):
        delete_bundle = make_transaction_bundle(
            method=TransactionMethod.DELETE,
            resources=resource_batch,
        )
        with server._sync_client() as client:
            server_response = client.post(
                server.api_address,
                json=json_dict(delete_bundle),
            )
            server_response.raise_for_status()
            delete_response.add_resource_ids(resource_batch)

    return delete_response


async def delete_async(
    server: "FhirServer",
    resources: List[Union[Resource, FHIRAbstractModel]] = None,
    references: List[Union[str, Reference]] = None,
    query: FhirQueryAsync = None,
) -> DeleteResponse:
    """Asynchrounously delete resources from the server while respecting referential integrity. This means
    that resources are deleted in reverse order of their dependencies, so that resources that depend on other
    resources are deleted before the resources they depend on.

    Args:
        server: The server to delete the resources from.
        resources: A list of resources to delete with ids assigned from server
        references: List of references to delete. Defaults to None.
        query: Query specifying the resources to delete. Defaults to None.
    """
    _validate_delete_args(resources, references, query)

    if query:
        delete_resources = await query.all().resources

    elif references:
        delete_resources = await server.get_many_async(references)
    else:
        delete_resources = resources
    delete_response = DeleteResponse(
        server=server.api_address,
        resource_ids=[],
    )

    for resource_batch in _resolve_delete_graph(delete_resources):
        delete_bundle = make_transaction_bundle(
            method=TransactionMethod.DELETE,
            resources=resource_batch,
        )
        async with server._async_client() as client:
            server_response = await client.post(
                server.api_address,
                json=json_dict(delete_bundle),
            )
            server_response.raise_for_status()
            delete_response.add_resource_ids(resource_batch)

    return delete_response


def _validate_delete_args(
    resources: List[Union[Resource, FHIRAbstractModel]] = None,
    references: List[Union[str, Reference]] = None,
    query: FhirQuerySync = None,
):
    if query and (resources or references):
        raise ValueError("Cannot specify both query and resources/references")
    if not (query or resources or references):
        raise ValueError("Must specify either query or resources/references")


def _resolve_delete_graph(resources: List[Union[Resource, FHIRAbstractModel]]):
    graph = reference_graph(resources)
    # reverse the graph so that resources that depend on other resources are deleted first
    graph = graph.reverse()

    nodes = list(graph.nodes)

    while len(nodes) > 0:
        top_nodes = [node for node in nodes if len(list(graph.predecessors(node))) == 0]
        resources = []
        for node in top_nodes:
            try:
                resources.append(resource_from_graph_node(graph, node))
            except Exception as e:
                print(f"Error creating resource from node {node}: {e}")
                print(graph.nodes[node]["resource"])
                raise e
        yield resources
        graph.remove_nodes_from(top_nodes)
        nodes = list(graph.nodes)
