from __future__ import annotations

from typing import TYPE_CHECKING, List, OrderedDict, Tuple, Union

import networkx as nx
import orjson
from fhir.resources import FHIRAbstractModel, construct_fhir_element
from fhir.resources.resource import Resource

from fhir_kindling.fhir_query import FhirQuerySync
from fhir_kindling.fhir_server.server_responses import (
    ResourceCreateResponse,
    TransferResponse,
)
from fhir_kindling.util.references import check_missing_references, extract_references

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


def reference_graph(resources: List[Union[Resource, FHIRAbstractModel]]) -> nx.DiGraph:
    """
    Creates a graph of the references in a list of resources.

    Args:
        resources: List of resource to create the graph from.

    Returns:
        A directed graph depicting the references in the resources.
    """
    dg = nx.DiGraph()
    for resource in resources:
        path = resource.relative_path()
        if path in dg:
            dg.nodes[path]["resource"] = resource
        else:
            dg.add_node(path, resource=resource)
        for reference in extract_references(resource):
            reference_path = f"{reference[1]}/{reference[2]}"
            if reference_path not in dg:
                dg.add_node(reference_path, resource=None)
            dg.add_edge(
                reference_path, path, field=reference[0], list_field=reference[3]
            )
    return dg


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
    while len(nodes) > 0:
        top_nodes = [node for node in nodes if len(list(graph.predecessors(node))) == 0]
        if display:
            print(f"Transferring - {len(top_nodes)} resources: {top_nodes}")

        # get the resources from the graph
        resources = [_resource_from_graph_node(graph, node) for node in top_nodes]
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


def _resource_from_graph_node(graph: nx.DiGraph, node: str) -> FHIRAbstractModel:
    """
    Get a resource from a graph node.

    Args:
        graph: The graph to get the resource from.
        node: The node to get the resource from.

    Returns:
        The resource at the node.
    """
    resource = graph.nodes[node]["resource"]
    if resource:
        if isinstance(resource, OrderedDict) or isinstance(resource, dict):
            resource_dict = dict(resource)
            resource_type = resource_dict.get(
                "resourceType", resource_dict.get("resource_type")
            )
            resource_json = orjson.dumps(resource_dict)
            resource = construct_fhir_element(resource_type, resource_json)
        elif isinstance(resource, FHIRAbstractModel):
            pass
        else:
            raise ValueError(f"Unknown resource type: {type(resource)}")
        return resource
    else:
        raise ValueError(f"Resource not found for node {node}")


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
