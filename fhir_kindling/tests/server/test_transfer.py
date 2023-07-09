import os

from fhir_kindling import FhirServer
from fhir_kindling.fhir_server.transfer import reference_graph, transfer


def test_reference_graph(fhir_server):
    """
    Test the reference graph
    """
    # get all conditions
    conditions = fhir_server.query("Condition").all().resource_list

    # get the reference graph
    graph = reference_graph(conditions)
    print("Nodes:")
    print(graph.nodes)

    print("Edges:")
    print(graph.edges)

    print("Graph:")
    print(graph.graph)

    assert len(graph.nodes) == len(conditions) * 2


def test_transfer_resources(fhir_server):
    """
    Test the transfer resources
    """
    # get all conditions
    conditions = fhir_server.query("Condition").all().resource_list

    target = FhirServer(api_address=os.getenv("TRANSFER_SERVER_URL"))

    response = transfer(source=fhir_server, target=target, resources=conditions)

    print(response)
    print(response.linkage)
    # save linkages
    response.save_linkage("linkage.json")

    os.remove("linkage.json")
