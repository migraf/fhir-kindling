from typing import Dict, List, Union

from fhir_kindling.benchmark.constants import BenchmarkOperations


class BenchmarkResults:
    def __init__(self):
        self.results = {}
        self._completed = False

    @property
    def completed(self):
        return self._completed

    def set_completed(self, completed: bool):
        self._completed = completed

    @property
    def insert_single(self) -> Union[List[float], Dict[str, List[float]]]:
        return self.results["insert"]

    @property
    def query(
        self,
    ) -> Dict[str, Dict[str, List[float]]]:
        return self.results["query"]

    @property
    def batch_insert(self) -> Union[List[float], Dict[str, List[float]]]:
        return self.results["batch_insert"]

    @property
    def dataset_insert(self) -> Union[List[float], Dict[str, List[float]]]:
        return self.results["dataset_insert"]

    @property
    def update(self) -> Union[List[float], Dict[str, List[float]]]:
        return self.results["update"]

    @property
    def delete(self) -> Union[List[float], Dict[str, List[float]]]:
        return self.results["delete"]

    @property
    def batch_delete(self) -> Union[List[float], Dict[str, List[float]]]:
        return self.results["batch_delete"]

    def add_result(
        self,
        operation: Union[str, BenchmarkOperations],
        server: str,
        results: Union[List[float], dict],
    ):
        if isinstance(operation, str):
            operation = BenchmarkOperations(operation)

        operation_results = self.results.get(operation.value, {})
        operation_results[server] = results
        self.results[operation] = operation_results

    def __repr__(self) -> str:
        return f"BenchmarkResults(completed={self.completed})"
