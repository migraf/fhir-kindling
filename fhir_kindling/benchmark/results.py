import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from fhir_kindling.benchmark.constants import BenchmarkOperations
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
    query_string: str
    result_count: int
    attempts: Optional[List[float]] = None


class SearchOperationResult(BenchmarkOperationResult):
    operation: BenchmarkOperations = BenchmarkOperations.SEARCH
    query_results: List[SearchQueryResult]


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
        use_enum_values = True


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


class BenchmarkResults:
    """Object to store, access and save the results of a benchmark."""

    def __init__(self):
        self.results = {}
        self._completed = False

    @property
    def completed(self):
        return self._completed

    def set_completed(self, completed: bool):
        self._completed = completed

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
            path = os.getcwd()
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2)

    @property
    def insert_single(self) -> Union[List[float], Dict[str, List[float]]]:
        return self.results["insert"]

    @property
    def query(
        self,
    ) -> Dict[str, Dict[str, List[float]]]:
        """
        Return the query results as a dictionary of server names to a list of queries and their execution times.
        """
        return self.results[BenchmarkOperations.SEARCH.value]

    @property
    def batch_insert(self) -> Union[List[float], Dict[str, List[float]]]:
        """Return the batch insert results as a dictionary of server names to a list of batch insert times."""
        return self.results[BenchmarkOperations.BATCH_INSERT.value]

    @property
    def dataset_insert(self) -> Union[List[float], Dict[str, List[float]]]:
        """Return the dataset insert results as a dictionary of server names to a list of dataset insert times."""
        return self.results[BenchmarkOperations.DATASET_INSERT.value]

    @property
    def update(self) -> Union[List[float], Dict[str, List[float]]]:
        """Return the update results as a dictionary of server names to a list of update times."""
        return self.results[BenchmarkOperations.UPDATE.value]

    @property
    def delete(self) -> Union[List[float], Dict[str, List[float]]]:
        """Return the delete results as a dictionary of server names to a list of delete times."""
        return self.results[BenchmarkOperations.DELETE.value]

    @property
    def batch_delete(self) -> Union[List[float], Dict[str, List[float]]]:
        """Return the batch delete results as a dictionary of server names to a list of batch delete times."""
        return self.results[BenchmarkOperations.BATCH_DELETE.value]

    @property
    def resources(self) -> Dict[str, Dict[str, List[float]]]:
        """Tracks the number of resources generated, queried, updated and deleted for each server."""
        pass

    def add_result(
        self,
        operation: Union[str, BenchmarkOperations],
        server: str,
        results: Union[List[float], dict],
    ):
        """Add results for a given operation and server.

        Args:
            operation: string or BenchmarkOperations enum value for the operation
            server: Name of the server
            results: the results to store
        """
        if isinstance(operation, str):
            operation = BenchmarkOperations(operation)

        operation_results = self.results.get(operation.value, {})
        operation_results[server] = results
        self.results[operation] = operation_results

    def __repr__(self) -> str:
        return f"BenchmarkResults(completed={self.completed})"
