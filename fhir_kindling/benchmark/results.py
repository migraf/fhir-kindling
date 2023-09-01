import os
from datetime import datetime
from typing import List, Optional, Union

import pandas as pd
import plotly.graph_objects as go
from pydantic import BaseModel, Field

from fhir_kindling.benchmark.constants import BenchmarkOperations
from fhir_kindling.benchmark.figures import (
    plot_benchmark_dataset,
    plot_benchmark_delete,
    plot_benchmark_insert,
    plot_benchmark_search,
    plot_benchmark_time_line,
    plot_benchmark_update,
)
from fhir_kindling.util.date_utils import local_now, to_iso_string


class BenchmarkOperationResult(BaseModel):
    """Object to store the results of a single benchmark operation."""

    operation: BenchmarkOperations
    attempts: Optional[List[float]] = None
    success: Optional[bool] = False
    start_time: datetime = Field(default_factory=local_now)
    end_time: Union[datetime, None]
    duration: Optional[float]
    error: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: to_iso_string(v),
        }
        use_enum_values = True


class SearchQueryResult(BaseModel):
    name: str
    query_string: str
    result_count: int
    attempts: Optional[List[float]] = None


class SearchOperationResult(BenchmarkOperationResult):
    operation: BenchmarkOperations = BenchmarkOperations.SEARCH
    query_results: Optional[List[SearchQueryResult]]


class ServerBenchmarkResult(BaseModel):
    """Object to store the results of a single benchmark operation."""

    name: str
    api_address: str
    completed: bool = False
    start_time: datetime = Field(default_factory=local_now)
    end_time: Optional[datetime]
    duration: Optional[float]
    operations: List[BenchmarkOperations]
    dataset_insert: Optional[BenchmarkOperationResult]
    single_insert: Optional[BenchmarkOperationResult]
    batch_insert: Optional[BenchmarkOperationResult]
    single_delete: Optional[BenchmarkOperationResult]
    batch_delete: Optional[BenchmarkOperationResult]
    single_update: Optional[BenchmarkOperationResult]
    batch_update: Optional[BenchmarkOperationResult]
    search: Optional[SearchOperationResult]

    class Config:
        json_encoders = {
            datetime: lambda v: to_iso_string(v),
        }

    def to_timeline_df(self) -> pd.DataFrame:
        """Return a dataframe with the timeline of operations."""
        timeline_list = []

        for operation in self.operation_list:
            entry = self._make_time_line_entry(operation)
            if entry:
                timeline_list.append(entry)

        return pd.DataFrame(timeline_list)

    def get_operation(
        self, operation: BenchmarkOperations
    ) -> Optional[BenchmarkOperationResult]:
        """Return the operation result for a given operation."""
        for operation_result in self.operation_list:
            if operation_result.operation == operation:
                return operation_result
        return None

    @property
    def operation_list(self) -> List[BenchmarkOperationResult]:
        return [
            self.dataset_insert,
            self.single_insert,
            self.batch_insert,
            self.search,
            self.single_update,
            self.batch_update,
            self.single_delete,
            self.batch_delete,
        ]

    def _make_time_line_entry(
        self, result: Union[BenchmarkOperationResult, None]
    ) -> Union[dict, None]:
        """Make a timeline entry for a given operation result."""

        if not result:
            return None

        operation_value = (
            result.operation.value
            if isinstance(result.operation, BenchmarkOperations)
            else result.operation
        )
        return dict(
            actor=self.name,
            operation=operation_value,
            start=result.start_time,
            end=result.end_time,
            duration=result.duration,
        )


class GeneratedResourceCount(BaseModel):
    """Object to store the results of a single benchmark operation."""

    resource_type: str
    count: int


class DataGenerationResult(BenchmarkOperationResult):
    operation: BenchmarkOperations = BenchmarkOperations.GENERATE
    resources_generated: List[GeneratedResourceCount]
    total_resources_generated: int


class BenchmarkResult(BaseModel):
    """Object to store the results of a full benchmark."""

    start_time: datetime = Field(default_factory=local_now)
    completed: bool = False
    end_time: Optional[datetime]
    duration: Optional[float]
    operations: List[BenchmarkOperations]
    data_generation_result: Optional[DataGenerationResult]
    server_results: List[ServerBenchmarkResult]

    class Config:
        json_encoders = {
            datetime: lambda v: to_iso_string(v),
        }

    def get_server_result(
        self, server_name: str = None, api_address: str = None
    ) -> Optional[ServerBenchmarkResult]:
        """Return the server result for a given server name or api address."""
        for server_result in self.server_results:
            if server_result.name == server_name:
                return server_result
            if server_result.api_address == api_address:
                return server_result
        return None

    def get_operation_for_server(
        self, server_name: str, operation: BenchmarkOperations
    ) -> Optional[BenchmarkOperationResult]:
        """Return the operation result for a given server name and operation."""
        server_result = self.get_server_result(server_name=server_name)
        if server_result:
            return server_result.get_operation(operation)
        return None

    def save(self, path: str = None):
        """Save the results of the benchmark as a json file.

        Args:
            path: Directory to save the results. If None defaults to current working directory
            figure: Whether to save the figure as a png file. Defaults to True.

        Returns:
            None
        """

        if not self.completed:
            raise ValueError(
                "Benchmark results not completed yet and can not be saved."
            )
        if not path:
            date_string = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")
            path = os.getcwd().join(f"benchmark_results_{date_string}.json")
        with open(path, "wb") as f:
            f.write(self.json(indent=2).encode("utf-8"))

    def save_plots(
        self, storage_dir: str = None, return_storage_dir: bool = False
    ) -> Union[str, None]:
        """Save the available plots of the benchmark as png files.

        Args:
            storage_dir: Directory to save the results. If None defaults to current working directory
            return_storage_dir: Whether to return the storage directory for the images

        Returns:
            None
        """

        dir_date_string = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")
        dir_name = f"benchmark_figures_{dir_date_string}"
        if not storage_dir:
            plot_dir = os.getcwd().join(dir_name)
        else:
            if not os.path.exists(storage_dir):
                raise ValueError(f"Path {dir} does not exist.")
            plot_dir = os.path.join(storage_dir, dir_name)
            os.mkdir(plot_dir)

        if not self.completed:
            raise ValueError(
                "Benchmark results not completed yet and can not be saved."
            )

        self._save_plots(plot_dir)

        if return_storage_dir:
            return plot_dir

    @classmethod
    def load(cls, path: str):
        """Load a benchmark result from a json file.

        Args:
            path: Path to the json file.

        Returns:
            BenchmarkResult
        """
        with open(path, "r") as f:
            return cls.parse_raw(f.read())

    def timeline_plot(self, show: bool = False) -> go.Figure:
        """Plot the timeline of the benchmark."""
        figure = plot_benchmark_time_line(self)
        if show:
            figure.show()
        return figure

    def dataset_plot(self, show: bool = False) -> go.Figure:
        figure = plot_benchmark_dataset(self)
        if show:
            figure.show()
        return figure

    def insert_plot(self, show: bool = False) -> go.Figure:
        figure = plot_benchmark_insert(self)
        if show:
            figure.show()
        return figure

    def update_plot(self, show: bool = False) -> go.Figure:
        figure = plot_benchmark_update(self)
        if show:
            figure.show()
        return figure

    def delete_plot(self, show: bool = False) -> go.Figure:
        figure = plot_benchmark_delete(self)
        if show:
            figure.show()
        return figure

    def search_plot(self, show: bool = False) -> go.Figure:
        figure = plot_benchmark_search(self)
        if show:
            figure.show()
        return figure

    def _save_plots(self, plot_dir: os.PathLike):
        if not os.path.exists(plot_dir):
            os.mkdir(plot_dir)

        ops = set(self.operations)
        for op in ops:
            if op == BenchmarkOperations.INSERT:
                insert_figure = self.insert_plot()
                insert_figure.write_image(os.path.join(plot_dir, "insert.png"))
            elif op == BenchmarkOperations.UPDATE:
                update_figure = self.update_plot()
                update_figure.write_image(os.path.join(plot_dir, "update.png"))
            elif op == BenchmarkOperations.DELETE:
                delete_figure = self.delete_plot()
                delete_figure.write_image(os.path.join(plot_dir, "delete.png"))
            elif op == BenchmarkOperations.SEARCH:
                search_figure = self.search_plot()
                search_figure.write_image(os.path.join(plot_dir, "search.png"))
            elif op == BenchmarkOperations.GENERATE:
                generate_figure = self.dataset_plot()
                generate_figure.write_image(os.path.join(plot_dir, "dataset.png"))

        timeline_figure = self.timeline_plot()
        timeline_figure.write_image(os.path.join(plot_dir, "timeline.png"))
