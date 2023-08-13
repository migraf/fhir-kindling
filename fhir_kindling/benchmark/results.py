import os
from datetime import datetime
from typing import List, Optional, Union

import pandas as pd
import plotly.graph_objects as go
from pydantic import BaseModel, Field

from fhir_kindling.benchmark.constants import BenchmarkOperations
from fhir_kindling.benchmark.figures import plot_benchmark_results
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

    name: Optional[str] = None
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

    @property
    def operation_list(self) -> List[BenchmarkOperationResult]:
        return [
            self.dataset_insert,
            self.single_insert,
            self.batch_insert,
            self.single_delete,
            self.batch_delete,
            self.search,
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
            path = os.getcwd().join(f"benchmark_results_{self.start_time}.json")
        with open(path, "w") as f:
            f.write(self.json(indent=2))

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

    def plot_results(self, show: bool = False) -> go.Figure:
        """Plot the results of the benchmark."""
        figure = plot_benchmark_results(self)
        if show:
            figure.show()
        return figure
