import os
import time
from typing import Any, List, Tuple, Union

import pendulum
from tqdm.autonotebook import tqdm

from fhir_kindling import FhirServer
from fhir_kindling.benchmark.constants import BenchmarkOperations, DefaultQueries
from fhir_kindling.benchmark.data import generate_benchmark_data
from fhir_kindling.benchmark.figures import plot_benchmark_results
from fhir_kindling.benchmark.results import BenchmarkResults
from fhir_kindling.fhir_query.query_parameters import FhirQueryParameters
from fhir_kindling.fhir_server.transfer import (
    reference_graph,
    resolve_reference_graph,
)
from fhir_kindling.generators import (
    PatientGenerator,
)

N_ATTEMPTS = 20
BATCH_SIZE = 100


class ServerBenchmark:
    steps: List[BenchmarkOperations]
    queries: List[Tuple[str, Union[str, FhirQueryParameters]]]

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
            steps: Select a subset of the steps to run. Defaults to None.

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
        self._results = BenchmarkResults()
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

        # if custom queries are provided use them, otherwise use the default queries
        if queries:
            self.queries = []
            for q in queries:
                if isinstance(q, str):
                    self.queries.append(FhirQueryParameters.from_query_string(q))
                elif isinstance(q, FhirQueryParameters):
                    self.queries.append(q)
                else:
                    raise ValueError(
                        "Custom_queries must be a list of fhir query strings or FhirQueryParameters objects"
                    )
        else:
            self.queries = [
                FhirQueryParameters.from_query_string(qs)
                for qs in [dfq.value for dfq in DefaultQueries]
            ]

    def run_suite(
        self, progress: bool = True, save: bool = True, results_dir: str = None
    ):
        """Run the the test suite configured for this benchmark instance.
        By default the steps are: Dataset generation, single resource insert, batch insert,
        dataset upload, search, update and delete.

        Args:
            progress: Wether to visualize progress using a progress bar. Defaults to True.
            save: Save the results to file once the suite is finished. Defaults to True.
            results_dir: Directory in which to save the results. If None defaults to current working directory.
        """
        # generate benchmark data
        if BenchmarkOperations.GENERATE in self.steps:
            self.dataset = self.dataset_generator.generate(display=progress)
            # remove the generate step from the list of steps to run
            self.steps.remove(BenchmarkOperations.GENERATE)

        # run the benchmark for each server
        for i, server in tqdm(
            enumerate(self.servers),
            desc=f"Running bechmarks for {len(self.servers)} servers:",
            disable=not progress,
            leave=False,
        ):
            name = None
            if self.server_names:
                name = self.server_names[i]
            self._benchmark_server(server, progress=progress, name=name)

        self._results.set_completed(True)
        if save:
            self._save(path=results_dir)

    def _benchmark_server(self, server: FhirServer, progress: bool, name: str = None):
        """Run the benchmark suite for a single server

        Args:
            server: The server to run the benchmark against
            progress: Whether to display a progress bar
            name: Optional name for the server. Defaults to None.
        """
        # Iterate over the benchmark steps
        for step in tqdm(
            self.steps,
            desc=f"Server {server.api_address}",
            disable=not progress,
            leave=False,
        ):
            server_name = name if name else server.api_address
            if step == BenchmarkOperations.GENERATE:
                pass
            if step == BenchmarkOperations.INSERT:
                self._benchmark_insert(
                    server,
                    server_name=server_name,
                )
            elif step == BenchmarkOperations.DATASET_INSERT:
                self._upload_dataset(server, server_name=server_name)
            elif step == BenchmarkOperations.QUERY:
                self._benchmark_search(server, server_name=server_name)
            elif step == BenchmarkOperations.UPDATE:
                pass  # TODO
            elif step == BenchmarkOperations.DELETE:
                self._benchmark_delete(server, server_name=server_name)

    @property
    def results(self):
        """Retunrs the results of the benchmark if the benchmark has completed.

        Raises:
            Exception: If the benchmark has not completed

        Returns:
            The results of the benchmark
        """
        if not self._results.completed:
            raise Exception("Benchmark not completed")
        return self._results

    def plot(self):
        """Plot the results of the benchmark

        Returns:
            The plotly figure displaying the results
        """
        fig = plot_benchmark_results(self.results)
        return fig

    def _upload_dataset(self, server: FhirServer, server_name: str):
        """Upload the generated dataset to the server and track the time it takes.

        Args:
            server: The server to upload to
            server_name: Name for the server
        """
        # create temp copy of dataset
        dataset = self.dataset.copy(deep=True)

        ds_graph = reference_graph(dataset.resources)
        start_time = time.perf_counter()
        added_resources, linkage = resolve_reference_graph(
            ds_graph, server, True, False
        )
        total = time.perf_counter() - start_time
        resource_refs = [r.reference.reference for r in added_resources]
        self._add_resource_refs_for_tracking(server=server, refs=resource_refs)
        self._results.add_result(
            BenchmarkOperations.DATASET_INSERT,
            server_name,
            total,
        )

    def _save(self, path: str = None):
        """Save the benchmark results and figure to file

        Args:
            path: Where to save the resulst. Defaults to current working directory.
        """
        self.results.save(path)
        figure = self.plot()
        if not path:
            figure_path = os.getcwd()
            datestring = pendulum.now().to_iso8601_string().replace(":", "_")
            figure_path = os.path.join(figure_path, f"benchmark_{datestring}.png")
            figure.write_image(figure_path)

    def _benchmark_insert(self, server: FhirServer, server_name: str):
        self._benchmark_insert_single(server, server_name)
        self._benchmark_batch_insert(server, server_name)

    def _benchmark_update(self, server: FhirServer):
        self._benchmark_update_single(server)
        self._benchmark_batch_update(server)

    def _benchmark_insert_single(self, server: FhirServer, server_name: str):
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
        self._results.add_result(
            BenchmarkOperations.INSERT,
            server_name,
            timings,
        )
        # track added resources for each server
        added_resources = self.benchmark_resources.get(server.api_address, [])
        added_resources.extend(added_resources)
        self.benchmark_resources[server.api_address] = added_resources

    def _benchmark_batch_insert(self, server: FhirServer, server_name: str):
        timings = []
        # run multiple attempts for inserting resources
        for _ in range(self.n_attempts):
            resources = PatientGenerator(n=self.batch_size).generate()
            start_time = time.perf_counter()
            response = server.add_all(resources)
            elapsed_time = time.perf_counter() - start_time
            timings.append(elapsed_time)
            # track the added resources
            self._add_resource_refs_for_tracking(
                server, [r.reference.reference for r in response.create_responses]
            )

        self._results.add_result(
            BenchmarkOperations.BATCH_INSERT,
            server_name,
            timings,
        )

    def _add_resource_refs_for_tracking(
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
            BenchmarkOperations.QUERY,
            server_name,
            results=query_results,
        )

    def _benchmark_delete(self, server: FhirServer, server_name: str):
        start_time = time.perf_counter()
        server_resource_refs = self.benchmark_resources.get(server.api_address, [])
        if not server_resource_refs:
            raise Exception("No resources to delete")
        # delete all resources
        server.delete(references=server_resource_refs)
        elapsed_time = time.perf_counter() - start_time

        self._results.add_result(
            BenchmarkOperations.DELETE,
            server_name,
            elapsed_time,
        )

    def _benchmark_update_single(self, server: FhirServer):
        pass

    def _benchmark_batch_update(self, server: FhirServer):
        pass
