from fhir_kindling.fhir_server.server_responses import ServerSummary
import plotly.express as px


def server_summary_plot(server_summary: ServerSummary) -> dict:
    """
    Generate a plotly plot of the server summary.

    Args:
        server_summary: The summary of the server.

    Returns:
        A dict containing the plotly plot.
    """

    sorted_resources = sorted(server_summary.available_resources, key=lambda x: x.count, reverse=True)
    fig = px.bar(
        x=[r.resource for r in sorted_resources],
        y=[r.count for r in sorted_resources],
        title="Server Resource Summary"
    )
    fig.show()
    return fig.to_dict()
