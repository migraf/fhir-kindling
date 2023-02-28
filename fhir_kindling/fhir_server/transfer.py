from typing import List, Union

import networkx as nx
from fhir.resources import FHIRAbstractModel
from fhir.resources.resource import Resource

from fhir_kindling.util.references import extract_references


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
