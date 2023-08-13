import os
import time
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
from fhir_kindling.benchmark.figures import plot_benchmark_results
from fhir_kindling.benchmark.results import (
    BenchmarkOperationResult,
    BenchmarkResult,
    DataGenerationResult,
    GeneratedResourceCount,
)
from fhir_kindling.fhir_query.query_parameters import FhirQueryParameters
from fhir_kindling.fhir_server.transfer import (
    reference_graph,
    resolve_reference_graph,
)
from fhir_kindling.generators.dataset import DataSet
from fhir_kindling.util.date_utils import (
    convert_to_local_datetime,
    local_now,
    to_iso_string,
)


class ServerBenchmark:
    steps: List[BenchmarkOperations]
    queries: List[Tuple[str, FhirQueryParameters]]
    _result: BenchmarkResult

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
        self.server_names = server_names
        self._result = None
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

        # if custom queries are provided use them, otherwise use the default queries

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

        benchmark_result = BenchmarkResult(server_results=[])

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
            name = None
            if self.server_names:
                name = self.server_names[i]
            server_result = run_server_benchmark(self, server, name, progress=progress)
            benchmark_result.server_results.append(server_result)

        benchmark_result.completed = True
        benchmark_result.end_time = local_now()
        benchmark_result.duration = (
            benchmark_result.end_time - benchmark_result.start_time
        ).total_seconds()
        self._result = benchmark_result

        if save:
            self._save(path=results_dir)

        return self._result

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
            start=start,
            end=end,
            duration=(end - start).total_seconds(),
            success=True,
            total_resources_generated=dataset.n_resources,
            resources_generated=[
                GeneratedResourceCount(resource_type=k, count=v)
                for k, v in dataset.resource_counts.items()
            ],
        )

        return dataset, result

    @property
    def result(self) -> BenchmarkResult:
        """Retunrs the results of the benchmark if the benchmark has completed.

        Raises:
            Exception: If the benchmark has not completed

        Returns:
            The results of the benchmark
        """
        if self._result is None:
            raise Exception("Benchmark not completed")
        return self._result

    def plot(self):
        """Plot the results of the benchmark

        Returns:
            The plotly figure displaying the results
        """
        fig = plot_benchmark_results(self.result)
        return fig

    def _upload_dataset(
        self, server: FhirServer, server_name: str
    ) -> BenchmarkOperationResult:
        """Upload the generated dataset to the server and track the time it takes.

        Args:
            server: The server to upload to
            server_name: Name for the server
        """

        dataset_upload_result = BenchmarkOperationResult(
            operation=BenchmarkOperations.DATASET_INSERT,
        )
        # create temp copy of dataset
        dataset = self.dataset.copy(deep=True)

        ds_graph = reference_graph(dataset.resources)
        start_time = time.perf_counter()
        added_resources, linkage = resolve_reference_graph(
            ds_graph, server, True, False
        )
        total = time.perf_counter() - start_time
        resource_refs = [r.reference.reference for r in added_resources]
        self.add_resource_refs_for_tracking(server=server, refs=resource_refs)

        dataset_upload_result.success = True
        dataset_upload_result.attempts = [total]
        dataset_upload_result.end_time = local_now()
        dataset_upload_result.duration = (
            dataset_upload_result.end_time - dataset_upload_result.start_time
        ).total_seconds()
        return dataset_upload_result

    def _save(self, path: str = None):
        """Save the benchmark results and figure to file

        Args:
            path: Where to save the results. Defaults to current working directory.
        """

        datestring = to_iso_string(datetime=convert_to_local_datetime(datetime.now()))

        if not path:
            path = os.getcwd()

        bench_result_path = os.path.join(path, f"benchmark_{datestring}.json")
        bench_figure_path = os.path.join(path, f"benchmark_{datestring}.png")
        self._result.save(bench_result_path)
        figure = self.plot()
        figure.write_image(bench_figure_path)

    def add_resource_refs_for_tracking(
        self, server: FhirServer, refs: Union[List[Any], Any]
    ):
        server_resources = self.benchmark_resources.get(server.api_address, [])
        if isinstance(refs, list):
            server_resources.extend(refs)
        else:
            server_resources.append(refs)
        self.benchmark_resources[server.api_address] = server_resources

    def _benchmark_search(self, server: FhirServer, server_name: str):
        query_results = {}
        for query in self.queries:
            query_attempts = []
            for _ in range(self.n_attempts):
                start_time = time.perf_counter()
                server.query(query_parameters=query).all()
                elapsed_time = time.perf_counter() - start_time
                query_attempts.append(elapsed_time)
            query_results[query.to_query_string()] = query_attempts

        self._results.add_result(
            BenchmarkOperations.SEARCH,
            server_name,
            results=query_results,
        )

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
                benchmark_queries.append((str(query), query.value))

        return benchmark_queries
