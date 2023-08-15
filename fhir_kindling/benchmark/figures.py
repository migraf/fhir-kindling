from typing import TYPE_CHECKING

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

if TYPE_CHECKING:
    from fhir_kindling.benchmark.results import BenchmarkResult


def plot_benchmark_time_line(results: "BenchmarkResult") -> go.Figure:
    generate_entry = dict(
        operation="Generate",
        start=results.data_generation_result.start_time,
        end=results.data_generation_result.end_time,
        actor="kindling",
    )

    timeline_list = [generate_entry]
    timeline_df = pd.DataFrame(timeline_list)

    # add each servers results to the timeline
    for server_result in results.server_results:
        timeline_df = pd.concat(
            [timeline_df, server_result.to_timeline_df()], ignore_index=True
        )

    fig = px.timeline(
        timeline_df,
        x_start="start",
        x_end="end",
        y="actor",
        color="actor",
        hover_name="operation",
        hover_data={
            "duration": ":.2f",
        },
    )

    # update the layout
    fig.update_layout(
        title_text="Benchmark Timeline",
        height=300,
        width=1000,
        # center title
        title_x=0.5,
    )

    # dont show y axis labels
    fig.update_yaxes(showticklabels=False, visible=False)

    return fig


def plot_benchmark_results(results: "BenchmarkResult") -> go.Figure:
    timeline = plot_benchmark_time_line(results)
    timeline.show()

    figure = setup_subplots(results)

    for trace in timeline.data:
        figure.add_trace(timeline.data[0], row=1, col=1)
    return figure


def setup_subplots(results: "BenchmarkResult") -> go.Figure:
    fig = make_subplots(
        rows=5,
        cols=1,
        subplot_titles=(
            "Resources Overview",
            "Single Insert",
            "Batch Insert",
            "Dataset Insert",
            "Update Single",
            "Search",
        ),
    )

    return fig


# def plot_benchmark_results(results: "BenchmarkResult") -> go.Figure:
#     """Create a multi-panel plotly figure that depicts the results of the benchmark. The figure displays
#     the timings for different crud & query operations and compares the timings across the different servers.

#     Args:
#         results: benchmark results
#     """
#     fig = make_subplots(
#         rows=5,
#         cols=1,
#         subplot_titles=(
#             "Resources Overview" "Single Insert",
#             "Batch Insert",
#             "Dataset Insert",
#             "Update Single",
#             "Search",
#         ),
#     )

#     add_single_insert_traces(fig, results)
#     add_batch_insert_traces(fig, results)
#     add_dataset_insert_traces(fig, results)
#     add_query_traces(fig, results)
#     add_delete_traces(fig, results)

#     fig.update_layout(
#         title_text="FHIR Server Benchmark Results",
#         height=1200,
#         width=1000,
#         showlegend=True,
#         legend_tracegroupgap=190,
#     )
#     return fig


# def add_resource_overview_trace(fig: go.Figure, results: "BenchmarkResults"):
#     """Generate a pie chart with the number of resources generated, queried, updated and deleted for the benchmark
#      and add it as a trace to the figure.

#     Args:
#         fig: Output figure
#         results: The benchmark results
#     """
#     pass


# def add_single_insert_traces(fig: go.Figure, results: "BenchmarkResults"):
#     """Create traces for each server detailing the timings for inserting a single resource

#     Args:
#         results: the results in which the data is stored

#     Returns:
#         List of plotly bar charts that depict the timings for each server
#     """
#     for server, result in results.insert_single.items():
#         tr = go.Bar(y=result, name=server, legendgroup="1")
#         fig.add_trace(tr, row=1, col=1)


# def add_batch_insert_traces(fig: go.Figure, results: "BenchmarkResults"):
#     """Create traces for each server detailing the timings for inserting a single resource

#     Args:
#         results: the results in which the data is stored

#     Returns:
#         List of plotly bar charts that depict the timings for each server
#     """
#     for server, result in results.batch_insert.items():
#         tr = go.Bar(y=result, name=server, legendgroup="2")
#         fig.add_trace(tr, row=2, col=1)


# def add_dataset_insert_traces(fig: go.Figure, results: "BenchmarkResults"):
#     """Create traces for each server detailing the timings for inserting a single resource

#     Args:
#         fig: _description_
#         results: _description_
#     """
#     ds_fig = go.Bar(
#         y=list(results.dataset_insert.values()),
#         x=list(results.dataset_insert.keys()),
#         name="Dataset Insert",
#     )
#     fig.add_trace(ds_fig, row=3, col=1)


# def add_query_traces(fig: go.Figure, results: "BenchmarkResults"):
#     query_results = results.query
#     queries = list(list(query_results.values())[0].keys())

#     for server, result in query_results.items():
#         # average time for each query
#         avg_times = [sum(result[q]) / len(result[q]) for q in queries]

#         tr = go.Bar(y=avg_times, x=queries, name=server, legendgroup="4")
#         fig.add_trace(tr, row=4, col=1)


# def add_delete_traces(fig: go.Figure, results: "BenchmarkResults"):
#     delete_results = results.delete
#     x = list(delete_results.keys())
#     y = list(delete_results.values())
#     tr = go.Bar(y=y, x=x, name="Delete", legendgroup="5")
#     fig.add_trace(tr, row=5, col=1)
