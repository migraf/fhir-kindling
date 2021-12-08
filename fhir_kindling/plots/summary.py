from typing import List, Dict, Callable
import plotly.express as px
from fhir.resources.resource import Resource

from fhir_kindling.fhir_server.server_responses import ServerSummary


def server_summary_plot(server_summary: ServerSummary, show: bool = True) -> dict:
    """
    Generate a plotly plot of the server summary displaying the number of available resources on the server.

    Args:
        server_summary: The summary of the server.

    Returns:
        A dict containing the plotly bar plot.
    """

    sorted_resources = sorted(server_summary.available_resources, key=lambda x: x.count, reverse=True)
    fig = px.bar(
        x=[r.resource for r in sorted_resources],
        y=[r.count for r in sorted_resources],
        title="Server Resource Summary"
    )
    if show:
        fig.show()
    return fig.to_dict()


def resource_summary_plot(resources: List[Resource], selected_fields: List[str] = None,
                          field_functions: List[Dict[str, Callable]] = None) -> dict:
    """
    Generate a plotly plot of the resource summary displaying the number of resources with the selected fields.

    Args:
        resources: The list of resources to plot.
        selected_fields: The list of fields to plot.

    Returns:
        A dict containing the plotly bar plot.
    """

    resource_counts = [len([r for r in resources if r.has_field(f)]) for f in selected_fields]
    fig = px.bar(
        x=selected_fields,
        y=resource_counts,
        title=f"{resources[0].get_resource_type()} Summary"
    )
    return fig.to_dict()
