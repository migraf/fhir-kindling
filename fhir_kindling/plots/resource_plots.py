from typing import List
import plotly.graph_objects as go
from fhir.resources.resource import Resource
import pandas as pd


def plot_resource_field(resources: List[Resource], field: str, title: str = None, plot_type: str = "bar") -> dict:
    """
    Plot a field of a resource.

    :param resources: Resources for which to plot the field
    :param field: Field to plot
    :param title: Title of the plot
    :param plot_type: Type of plot to use. Options are: bar, histogram, pie
    :return: Plotly figure
    """
    if title is None:
        title = f"{field} for {resources[0].resource.resource_type}"

    figure = go.Figure()
    figure.update_layout(title_text=title, title_x=0.5)
    values = [resource.dict().get("resource").get(field) for resource in resources]
    # convert to series and get value counts
    val_counts = pd.Series(values).value_counts()
    if plot_type == "bar":
        figure.add_trace(go.Bar(
            x=val_counts.index,
            y=val_counts.values,
            name=field
        ))
    elif plot_type == "pie":
        figure.add_trace(go.Pie(
            labels=val_counts.index,
            values=val_counts.values,
            name=field
        ))

    figure.show()

    return figure.to_dict()
