from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Union

import networkx as nx
import orjson
from fhir.resources import FHIRAbstractModel
from fhir.resources.resource import Resource
from tqdm.autonotebook import tqdm

from fhir_kindling.fhir_query import FhirQuerySync
from fhir_kindling.fhir_server.server_responses import (
    ResourceCreateResponse,
    TransferResponse,
)
from fhir_kindling.util.references import (
    check_missing_references,
    reference_graph,
    resource_from_graph_node,
)

if TYPE_CHECKING:
    from fhir_kindling.fhir_server import FhirServer


def transfer(
    source: "FhirServer",
    target: "FhirServer",
    resources: List[Union[Resource, FHIRAbstractModel]] = None,
    query: FhirQuerySync = None,
    get_missing: bool = True,
    record_linkage: bool = True,
    display: bool = True,
) -> TransferResponse:
    """
    Transfer a list of resources from one server to another.

    Args:
        source: The server to transfer the resources from.
        target: The server to transfer the resources to.
        resources: A list of resources to transfer.
        query: A FhirQuerySync object to use to query the source server.
        get_missing: Whether to get missing resources from the source server.
        record_linkage: Whether to record the linkage between the source and target resources.
        display: Whether to display a progress bar.
    """

    # get the resources to transfer, including missing references
    transfer_resources = _get_transfer_resources(source, resources, query, get_missing)
    transfer_graph = reference_graph(transfer_resources)

    # process the graph to create the resources on the target server
    create_responses, linkage = resolve_reference_graph(
        transfer_graph, target, record_linkage, display
    )

    return TransferResponse(
        origin_server=source.api_address,
        destination_server=target.api_address,
        create_responses=create_responses,
        linkage=linkage,
    )


def resolve_reference_graph(
    graph: nx.DiGraph,
    target: "FhirServer",
    record_linkage: bool,
    display: bool,
) -> Tuple[List[ResourceCreateResponse], dict]:
    nodes = list(graph.nodes)

    linkage = {}
    create_responses = []
    # iterate over the graph and update the references off all successors node to match the newly created resources
    # on the target server

    with tqdm(total=len(nodes), disable=not display) as pbar:
        while len(nodes) > 0:
            top_nodes = [
                node for node in nodes if len(list(graph.predecessors(node))) == 0
            ]
            # get the resources from the graph
            resources = []

            for node in top_nodes:
                try:
                    resources.append(resource_from_graph_node(graph, node))
                except Exception as e:
                    print(e)
                    print(node)
                    raise e
            # insert the resources into the target server
            create_response = target.add_all(resources=resources)

            # iterate through the top nodes and update the successors with the references from the target server
            for node, reference in zip(top_nodes, create_response.references):
                if record_linkage:
                    hash_origin = hash(node)
                    linkage[hash_origin] = reference.reference
                _update_successors(graph, node, reference.reference)

            # add the create response to the list of responses
            create_responses.extend(create_response.create_responses)

            # remove the processed top nodes from the graph
            graph.remove_nodes_from(top_nodes)
            nodes = list(graph.nodes)
            pbar.update(len(top_nodes))

    return create_responses, linkage


def _update_successors(graph: nx.DiGraph, node: str, reference: str):
    """
    Update the successors of a node in a graph with the updated reference from the new server.

    Args:
        graph: The graph to update.
        node: The node to update.
        reference: The reference to update the node with.
    """
    for successor in graph.successors(node):
        field = graph[node][successor]["field"]
        list_field = graph[node][successor]["list_field"]
        resource = graph.nodes[successor]["resource"]

        if list_field:
            # Find the item that references the node
            reference_list = graph.nodes[successor]["resource"].dict()[field]
            reference_item = next(
                (item for item in reference_list if item.get("reference") == str(node)),
                None,
            )
            if reference_item:
                # update the resource with the new reference
                index = reference_list.index(reference_item)
                resource = orjson.loads(resource.json())
                resource[field][index] = {"reference": reference}
                graph.nodes[successor]["resource"] = resource
            else:
                print("Reference item not found")
        else:
            if not isinstance(graph.nodes[successor]["resource"], dict):
                resource = orjson.loads(resource.json())
                resource[field] = {"reference": reference}
                graph.nodes[successor]["resource"] = resource
            else:
                graph.nodes[successor]["resource"][field] = reference


def _get_transfer_resources(
    source: "FhirServer",
    resources: List[Union[Resource, FHIRAbstractModel]] = None,
    query: FhirQuerySync = None,
    get_missing: bool = True,
) -> List[FHIRAbstractModel]:
    if query and resources:
        raise ValueError("Cannot specify both query and resources")
    if not query and not resources:
        raise ValueError(
            f"Must specify either query or resources. Query: {query}, Resources: {resources}"
        )
    # if query parameters are given execute the query against the server
    if query:
        resources = query.all().resource_list
    # find missing references
    missing_references = check_missing_references(resources)

    # get missing references
    if missing_references:
        if get_missing:
            missing = source.get_many(missing_references)
            resources.extend(missing)
        else:
            raise ValueError(
                f"Related resources of the resources to be transferred are missing:\n{missing_references} \n\n"
                f"To get these resources, set get_missing=True."
            )

    return resources
