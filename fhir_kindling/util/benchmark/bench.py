import time
from enum import Enum
from typing import Any, Dict, List, Union

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding

from fhir_kindling import FhirServer
from fhir_kindling.generators import (
    PatientGenerator,
)
from fhir_kindling.util.benchmark.figures import plot_benchmark_results

N_ATTEMPTS = 20
BATCH_SIZE = 100

COVID_CODE = CodeableConcept(
    coding=[
        Coding(
            system="http://id.who.int/icd/release/11/mms",
            code="RA01.0",
            display="COVID-19, virus identified",
        )
    ],
    text="COVID-19",
)


class ServerBenchmark:
    def __init__(
        self,
        servers: List[FhirServer],
        n_attempts: int = N_ATTEMPTS,
        batch_size: int = BATCH_SIZE,
    ):
        self.servers = servers
        self._results = BenchmarkResults()
        self.benchmark_resources = {}
        self.n_attempts = n_attempts
        self.batch_size = batch_size

    def run(self):
        for server in self.servers:
            print(f"Running benchmarks for {server.api_address}")
            self._benchmark_insert(server)
            self._benchmark_query(server)

        print("Benchmark complete")
        self._results.set_completed(True)

    @property
    def results(self):
        if not self._results.completed:
            raise Exception("Benchmark not completed")
        return self._results

    @property
    def results_df(self):
        return self._results.to_df()

    def plot_results(self):
        plot_benchmark_results(self.results)

    def _benchmark_insert(self, server: FhirServer):
        self._benchmark_insert_single(server)
        self._benchmark_batch_insert(server)

    def _benchmark_insert_single(self, server: FhirServer):
        print(f"Running single insert benchmark for {server.api_address}")
        resources = PatientGenerator(n=self.n_attempts).generate()

        timings = []
        added_resources = []
        for resource in resources:
            start_time = time.perf_counter()
            result = server.add(resource)
            added_resources.append(result.reference)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            timings.append(total_time)
        print(
            f"Average time inserting single resource for server({server.api_address}): "
            f"{sum(timings) / len(timings):.4f} seconds"
        )
        self._results.add_result(
            BenchmarkOperations.INSERT, server.api_address, timings
        )
        # track added resources for each server
        added_resources = self.benchmark_resources.get(server.api_address, [])
        added_resources.extend(added_resources)
        self.benchmark_resources[server.api_address] = added_resources

    def _benchmark_batch_insert(self, server: FhirServer):
        print(f"Running batch insert benchmark for {server.api_address}")
        resources = PatientGenerator(n=self.batch_size).generate()

        timings = []
        # run multiple attempts for inserting resources
        for _ in range(self.n_attempts):
            start_time = time.perf_counter()
            response = server.add_all(resources)
            elapsed_time = time.perf_counter() - start_time
            timings.append(elapsed_time)
            # track the added resources
            self._add_resource_refs_for_tracking(
                server, [r.reference for r in response.create_responses]
            )

        print(
            f"Average time inserting batch of resources for server({server.api_address}): "
            f"{sum(timings) / len(timings):.4f} seconds"
        )
        self._results.add_result(
            BenchmarkOperations.BATCH_INSERT, server.api_address, timings
        )

    def _add_resource_refs_for_tracking(
        self, server: FhirServer, resource: Union[List[Any], Any]
    ):
        server_resources = self.benchmark_resources.get(server.api_address, [])
        if isinstance(resource, list):
            server_resources.extend(resource)
        else:
            server_resources.append(resource)
        self.benchmark_resources[server.api_address] = server_resources

    def _benchmark_query(self, server):
        pass


class BenchmarkOperations(str, Enum):
    INSERT = "insert"
    QUERY = "query"
    BATCH_INSERT = "batch_insert"
    BATCH_QUERY = "batch_query"
    UPDATE = "update"
    DELETE = "delete"
    BATCH_DELETE = "batch_delete"


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
    def query(self) -> Union[List[float], Dict[str, List[float]]]:
        return self.results["query"]

    @property
    def batch_insert(self) -> Union[List[float], Dict[str, List[float]]]:
        return self.results["batch_insert"]

    @property
    def batch_query(self) -> Union[List[float], Dict[str, List[float]]]:
        return self.results["batch_query"]

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
        results: List[float],
    ):
        if isinstance(operation, str):
            operation = BenchmarkOperations(operation)

        operation_results = self.results.get(operation.value, {})
        operation_results[server] = results
        self.results[operation] = operation_results

    def __repr__(self) -> str:
        return f"BenchmarkResults(completed={self.completed})"