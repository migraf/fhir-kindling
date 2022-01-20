import plotly.express as px

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

