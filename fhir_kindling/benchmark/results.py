import json
import os
from typing import Dict, List, Union

import pendulum

from fhir_kindling.benchmark.constants import BenchmarkOperations


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

        date_string = pendulum.now().to_iso8601_string().replace(":", "_")
        file_name = f"benchmark_results_{date_string}.json"
        file_path = os.path.join(path, file_name)
        with open(file_path, "w") as f:
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
        return self.results[BenchmarkOperations.QUERY.value]

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
