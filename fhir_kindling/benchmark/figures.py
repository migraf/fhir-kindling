from typing import TYPE_CHECKING, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from fhir_kindling.benchmark.constants import BenchmarkOperations

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


def plot_benchmark_dataset(results: "BenchmarkResult") -> go.Figure:
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=["Resources Generated", "Dataset Upload Time"],
    )

    # bar chart for resources generated
    labels = [
        r.resource_type for r in results.data_generation_result.resources_generated
    ]
    values = [r.count for r in results.data_generation_result.resources_generated]

    resource_generated_bar_chart = go.Bar(
        x=labels,
        y=values,
    )

    fig.add_trace(
        resource_generated_bar_chart,
        row=1,
        col=1,
    )

    # bar chart for dataset upload
    names = [sr.name for sr in results.server_results]
    dataset_upload_time = [sr.dataset_insert.duration for sr in results.server_results]

    dataset_upload_bar_chart = go.Bar(
        x=names,
        y=dataset_upload_time,
    )

    fig.add_trace(
        dataset_upload_bar_chart,
        row=1,
        col=2,
    )

    # update the layout
    fig.update_layout(
        title_text="Benchmark Dataset",
        height=400,
        width=1000,
        # center title
        title_x=0.5,
        showlegend=False,
    )

    return fig


def plot_benchmark_insert(results: "BenchmarkResult") -> go.Figure:
    fig = single_and_batch_plot(
        results,
        BenchmarkOperations.INSERT,
        BenchmarkOperations.BATCH_INSERT,
        "Benchmark Update",
        ["Single Update", "Batch Update"],
    )

    return fig


def plot_benchmark_update(results: "BenchmarkResult") -> go.Figure:
    fig = single_and_batch_plot(
        results,
        BenchmarkOperations.UPDATE,
        BenchmarkOperations.BATCH_UPDATE,
        "Benchmark Update",
        ["Single Update", "Batch Update"],
    )

    return fig


def plot_benchmark_delete(results: "BenchmarkResult") -> go.Figure:
    fig = single_and_batch_plot(
        results,
        BenchmarkOperations.DELETE,
        BenchmarkOperations.BATCH_DELETE,
        "Benchmark Delete",
        ["Single Delete", "Batch Delete"],
    )

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=["Single Delete", "Batch Delete"],
    )

    return fig


def plot_benchmark_search(results: "BenchmarkResult") -> go.Figure:
    # todo implement this

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=["Single Delete", "Batch Delete"],
    )

    return fig


def single_and_batch_plot(
    results: "BenchmarkResult",
    single_op: BenchmarkOperations,
    batch_op: BenchmarkOperations,
    plot_title: str,
    subplot_titles: List[str],
) -> go.Figure:
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=subplot_titles,
    )

    for server_result in results.server_results:
        single_result = results.get_operation_for_server(server_result.name, single_op)
        if single_result:
            single_chart = make_line_chart_from_attempts(
                single_result.attempts, server_result.name
            )
            fig.add_trace(
                single_chart,
                row=1,
                col=1,
            )

        batch_result = results.get_operation_for_server(server_result.name, batch_op)
        if batch_result:
            batch_chart = make_line_chart_from_attempts(
                batch_result.attempts, server_result.name
            )
            fig.add_trace(
                batch_chart,
                row=1,
                col=2,
            )

    # update the layout
    fig.update_layout(
        title_text=plot_title,
        height=400,
        width=1000,
        # center title
        title_x=0.5,
    )
    return fig


def make_line_chart_from_attempts(attempts: List[float], name: str) -> go.Figure:
    trace = go.Scatter(
        x=list(range(len(attempts))),
        y=attempts,
        mode="lines+markers",
        name=name,
    )

    return trace
