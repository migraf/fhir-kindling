from typing import TYPE_CHECKING

import plotly.graph_objects as go
from plotly.subplots import make_subplots

if TYPE_CHECKING:
    from fhir_kindling.benchmark.results import BenchmarkResults


def plot_benchmark_results(results: "BenchmarkResults") -> go.Figure:
    """Create a multi-panel plotly figure that depicts the results of the benchmark. The figure displays
    the timings for different crud & query operations and compares the timings across the different servers.

    Args:
        results: benchmark results
    """
    fig = make_subplots(
        rows=5,
        cols=1,
        subplot_titles=(
            "Single Insert",
            "Batch Insert",
            "Dataset Insert" "Update Single",
            "Search",
        ),
    )

    add_single_insert_traces(fig, results)
    add_batch_insert_traces(fig, results)
    add_dataset_insert_traces(fig, results)
    add_query_traces(fig, results)

    fig.update_layout(
        title_text="FHIR Server Benchmark Results",
        height=1200,
        width=1000,
        showlegend=True,
        legend_tracegroupgap=190,
    )
    return fig


def add_single_insert_traces(fig: go.Figure, results: "BenchmarkResults"):
    """Create traces for each server detailing the timings for inserting a single resource

    Args:
        results: the results in which the data is stored

    Returns:
        List of plotly bar charts that depict the timings for each server
    """
    for server, result in results.insert_single.items():
        tr = go.Bar(y=result, name=server, legendgroup="1")
        fig.add_trace(tr, row=1, col=1)


def add_batch_insert_traces(fig: go.Figure, results: "BenchmarkResults"):
    """Create traces for each server detailing the timings for inserting a single resource

    Args:
        results: the results in which the data is stored

    Returns:
        List of plotly bar charts that depict the timings for each server
    """
    for server, result in results.batch_insert.items():
        tr = go.Bar(y=result, name=server, legendgroup="2")
        fig.add_trace(tr, row=2, col=1)


def add_dataset_insert_traces(fig: go.Figure, results: "BenchmarkResults"):
    """Create traces for each server detailing the timings for inserting a single resource

    Args:
        fig: _description_
        results: _description_
    """
    ds_fig = go.Bar(
        y=list(results.dataset_insert.values()),
        x=list(results.dataset_insert.keys()),
    )
    fig.add_trace(ds_fig, row=3, col=1)


def add_query_traces(fig: go.Figure, results: "BenchmarkResults"):
    query_results = results.query
    queries = list(list(query_results.values())[0].keys())

    for server, result in query_results.items():
        # average time for each query
        avg_times = [sum(result[q]) / len(result[q]) for q in queries]

        tr = go.Bar(y=avg_times, x=queries, name=server, legendgroup="4")
        fig.add_trace(tr, row=4, col=1)
