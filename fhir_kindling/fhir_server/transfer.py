from __future__ import annotations

from typing import List, Union, Tuple

import networkx as nx
from fhir.resources import FHIRAbstractModel
from fhir.resources.resource import Resource
from fhir_kindling.fhir_query import FhirQuerySync, FhirQueryAsync

from fhir_kindling.util.references import extract_references, check_missing_references

from typing import TYPE_CHECKING

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
):
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

    transfer_resources = _get_transfer_resources(source, resources, query, get_missing)


def _get_transfer_resources(
        source: "FhirServer",
        resources: List[Union[Resource, FHIRAbstractModel]] = None,
        query: FhirQuerySync = None,
        get_missing: bool = True,
) -> List[FHIRAbstractModel]:

    if resources:
        transfer_resources = resources
    elif query:
        transfer_resources = query.all().resource_list
    else:
        raise ValueError("Either resources or query must be provided.")

    # check for missing references
    missing_references = check_missing_references(transfer_resources)

    # get missing references
    if missing_references:
        if get_missing:
            missing = source.get_many(missing_references)
            transfer_resources.extend(missing)
        else:
            raise ValueError(
                f"Related resources of the resources to be transferred are missing:\n{missing_references} \n\n"
                f"To get these resources, set get_missing=True."
            )

    return transfer_resources













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
