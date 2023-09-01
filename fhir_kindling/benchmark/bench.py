import os
import uuid
from datetime import datetime
from typing import Any, List, Tuple, Union

from tqdm.autonotebook import tqdm

from fhir_kindling import FhirServer
from fhir_kindling.benchmark.benchmark_server import run_server_benchmark
from fhir_kindling.benchmark.constants import (
    BATCH_SIZE,
    N_ATTEMPTS,
    BenchmarkOperations,
    DefaultQueries,
)
from fhir_kindling.benchmark.data import generate_benchmark_data
from fhir_kindling.benchmark.results import (
    BenchmarkResult,
    DataGenerationResult,
    GeneratedResourceCount,
)
from fhir_kindling.fhir_query.query_parameters import FhirQueryParameters
from fhir_kindling.generators.dataset import DataSet
from fhir_kindling.util.date_utils import (
    convert_to_local_datetime,
    local_now,
    to_iso_string,
)


class ServerBenchmark:
    steps: List[BenchmarkOperations]
    queries: List[Tuple[str, FhirQueryParameters]]
    result: BenchmarkResult

    def __init__(
        self,
        servers: List[FhirServer],
        server_names: Union[List[str], None] = None,
        n_attempts: int = N_ATTEMPTS,
        batch_size: int = BATCH_SIZE,
        dataset_size: int = 1000,
        custom_queries: Union[
            List[Tuple[str, Union[str, FhirQueryParameters]]], None
        ] = None,
        steps: List[Union[str, BenchmarkOperations]] = None,
    ):
        """Initialize a benchmark object to test the performance of a set of servers.

        Args:
            servers: List of servers to benchmark.
            server_names: Optionally provide a list of names for the servers. Which will be used in the results.
                Defaults to the servers api address.
            n_attempts: The number of attempts for each operation. Defaults to N_ATTEMPTS.
            batch_size: The size of the batches for evaluating batch operations. Defaults to BATCH_SIZE.
            dataset_size: The number of base resources in the dataset. Defaults to 1000.
            custom_queries: A list of custom FHIR search queries to be included in the benchmark. Defaults to None.
            steps: Select a subset of the steps to run. If no st. E.g.
                ["data_generation", "single_insert", "search"]

        Raises:
            ValueError: If the number of server names does not match the number of servers.
            Or if steps or custom_queries are not valid.
        """
        self.servers = servers

        if server_names and len(server_names) != len(servers):
            raise ValueError(
                f"Invalid server names len={len(server_names)}, and len server = {len(servers)} "
                "When providing server_names, must provide one for each server"
            )
        if server_names is None:
            server_names = [str(uuid.uuid4())[:8] for _ in servers]
        self.server_names = server_names
        self.result = None
        self.benchmark_resources = {}
        self.n_attempts = n_attempts
        self.batch_size = batch_size
        self.dataset = None

        self._setup(queries=custom_queries, steps=steps)
        self.dataset_generator = generate_benchmark_data(n_patients=dataset_size)

    def _setup(
        self,
        queries: Union[List[Tuple[str, Union[str, FhirQueryParameters]]], None] = None,
        steps: List[Union[str, BenchmarkOperations]] = None,
    ):
        """Set up the steps and custom queries for the benchmark.

        Args:
            queries: User submitted list of queries to include. Defaults to None.
            steps: User submitted subset of benchmark steps to perform. Defaults to None.

        Raises:
            ValueError: If the operations/steps given are invalid
            ValueError: If any of the queries given is invalid
        """
        # if a list of steps is provided run only these steps, otherwise run all steps
        if steps:
            self.steps = []
            for s in steps:
                if isinstance(s, str):
                    self.steps.append(BenchmarkOperations(s))
                elif isinstance(s, BenchmarkOperations):
                    self.steps.append(s)
                else:
                    raise ValueError(
                        "Steps must be a list of strings or BenchmarkOperations objects"
                    )
        else:
            self.steps = [BenchmarkOperations(step) for step in BenchmarkOperations]

        self._order_benchmark_steps()
        self.queries = self._setup_queries(queries)

    def run_suite(
        self, progress: bool = True, save: bool = True, results_dir: str = None
    ) -> BenchmarkResult:
        """Run the the test suite configured for this benchmark instance.
        By default the steps are: Dataset generation, single resource insert, batch insert,
        dataset upload, search, update and delete.

        Args:
            progress: Wether to visualize progress using a progress bar. Defaults to True.
            save: Save the results to file once the suite is finished. Defaults to True.
            results_dir: Directory in which to save the results. If None defaults to current working directory.
        """

        benchmark_result = BenchmarkResult(server_results=[], operations=self.steps)

        # generate benchmark data if the benchmark data generation step is included
        if BenchmarkOperations.GENERATE in self.steps:
            dataset, data_generation_result = self._run_dateset_generator(
                progress=progress
            )
            benchmark_result.data_generation_result = data_generation_result
            self.dataset = dataset
            # remove the data generation step from the steps to run
            self.steps.remove(BenchmarkOperations.GENERATE)

        # run the benchmark for each server
        for i, server in tqdm(
            enumerate(self.servers),
            desc=f"Running bechmarks for {len(self.servers)} servers:",
            disable=not progress,
        ):
            server_result = run_server_benchmark(
                self, server, self.server_names[i], progress=progress
            )
            benchmark_result.server_results.append(server_result)

        benchmark_result.completed = True
        benchmark_result.end_time = local_now()
        benchmark_result.duration = (
            benchmark_result.end_time - benchmark_result.start_time
        ).total_seconds()
        self.result = benchmark_result

        if save:
            self._save(path=results_dir)

        return self.result

    def _run_dateset_generator(
        self, progress: bool
    ) -> Tuple[DataSet, DataGenerationResult]:
        """Run the dataset generator and return the generated dataset.

        Args:
            progress: Whether to display a progress bar

        """
        start = local_now()
        dataset = self.dataset_generator.generate(display=progress)
        end = local_now()

        result = DataGenerationResult(
            start_time=start,
            end_time=end,
            duration=(end - start).total_seconds(),
            success=True,
            total_resources_generated=dataset.n_resources,
            resources_generated=[
                GeneratedResourceCount(resource_type=k, count=v)
                for k, v in dataset.resource_counts.items()
            ],
        )

        return dataset, result

    def _save(self, path: str = None):
        """Save the benchmark results and figure to file

        Args:
            path: Where to save the results. Defaults to current working directory.
        """

        datestring = to_iso_string(
            datetime=convert_to_local_datetime(datetime.now())
        ).replace(":", "-")

        if not path:
            path = os.getcwd()

        bench_result_path = os.path.join(path, f"benchmark_{datestring}.json")
        self.result.save(bench_result_path)

    def add_resource_refs_for_tracking(
        self, server: FhirServer, refs: Union[List[Any], Any]
    ):
        server_resources = self.benchmark_resources.get(server.api_address, [])
        if isinstance(refs, list):
            server_resources.extend(refs)
        else:
            server_resources.append(refs)
        self.benchmark_resources[server.api_address] = server_resources

    def _order_benchmark_steps(self):
        """Order the benchmark steps based on the dependencies between them"""
        # order the steps
        # (if dataset upload is included, it must be run before search)
        # delete operations must be run last
        if BenchmarkOperations.DATASET_INSERT in self.steps:
            self.steps.remove(BenchmarkOperations.DATASET_INSERT)
            self.steps.insert(0, BenchmarkOperations.DATASET_INSERT)

        if BenchmarkOperations.DELETE in self.steps:
            self.steps.remove(BenchmarkOperations.DELETE)
            self.steps.append(BenchmarkOperations.DELETE)

        if BenchmarkOperations.BATCH_DELETE in self.steps:
            self.steps.remove(BenchmarkOperations.BATCH_DELETE)
            self.steps.append(BenchmarkOperations.BATCH_DELETE)

    def _setup_queries(
        self,
        queries: Union[List[Tuple[str, Union[str, FhirQueryParameters]]], None] = None,
    ) -> List[Tuple[str, FhirQueryParameters]]:
        """Setup the queries to be used for benchmarking"""
        # if no queries are specified, generate a default set of queries

        benchmark_queries = []
        if queries:
            for name, q in queries:
                if isinstance(q, str):
                    benchmark_queries.append(
                        (name, FhirQueryParameters.from_query_string(q))
                    )
                elif isinstance(q, FhirQueryParameters):
                    benchmark_queries.append((name, q))
                else:
                    raise ValueError(
                        "Custom_queries must be a list of fhir query strings or FhirQueryParameters objects"
                    )
        else:
            for query in DefaultQueries:
                benchmark_queries.append(
                    (str(query), FhirQueryParameters.from_query_string(query.value))
                )

        return benchmark_queries
