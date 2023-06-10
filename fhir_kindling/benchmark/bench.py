import time
from typing import Any, List, Union

from tqdm import tqdm

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
    def __init__(
        self,
        servers: List[FhirServer],
        server_names: Union[List[str], None] = None,
        n_attempts: int = N_ATTEMPTS,
        batch_size: int = BATCH_SIZE,
        dataset_size: int = 1000,
        custom_queries: Union[List[Union[str, FhirQueryParameters]], None] = None,
        steps: List[Union[str, BenchmarkOperations]] = None,
    ):
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
        self.queries = []
        self.dataset = None
        self.generated_resource_refs: List[str] = []
        # if a list of steps is provided run only these steps, otherwise run all steps
        if steps:
            self.steps = steps
        else:
            self.steps = list(BenchmarkOperations)

        # if custom queries are provided use them, otherwise use the default queries
        if custom_queries:
            for q in custom_queries:
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

        self.dataset_generator = generate_benchmark_data(n_patients=dataset_size)

        # print(self.dataset)

        # self.dataset_generator.explain()
        # self.dataset_generator.generate()

    def run_suite(self, progress: bool = True):
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
            # Iterate over the benchmark steps
            for step in tqdm(
                self.steps,
                desc=f"Server {server.api_address}",
                disable=not progress,
                leave=False,
            ):
                if step == BenchmarkOperations.GENERATE:
                    pass
                if step == BenchmarkOperations.INSERT:
                    self._benchmark_insert(
                        server,
                        server_name=self.server_names[i] if self.server_names else None,
                    )
                elif step == BenchmarkOperations.DATASET_INSERT:
                    self._upload_dataset(server)
                elif step == BenchmarkOperations.QUERY:
                    self._benchmark_search(server)
                elif step == BenchmarkOperations.UPDATE:
                    pass  # TODO
                elif step == BenchmarkOperations.DELETE:
                    pass  # TODO

        self._results.set_completed(True)
        self.plot().show()

    @property
    def results(self):
        if not self._results.completed:
            raise Exception("Benchmark not completed")
        return self._results

    @property
    def results_df(self):
        return self._results.to_df()

    def plot(self):
        fig = plot_benchmark_results(self.results)
        return fig

    def _upload_dataset(self, server: FhirServer):
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
            server.api_address,
            total,
        )

    def _benchmark_insert(self, server: FhirServer, server_name: str = None):
        self._benchmark_insert_single(server, server_name)
        self._benchmark_batch_insert(server)

    def _benchmark_update(self, server: FhirServer):
        self._benchmark_update_single(server)
        self._benchmark_batch_update(server)

    def _benchmark_insert_single(self, server: FhirServer, server_name: str = None):
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
            server_name if server_name else server.api_address,
            timings,
        )
        # track added resources for each server
        added_resources = self.benchmark_resources.get(server.api_address, [])
        added_resources.extend(added_resources)
        self.benchmark_resources[server.api_address] = added_resources

    def _benchmark_batch_insert(self, server: FhirServer, server_name: str = None):
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
            server_name if server_name else server.api_address,
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

    def _benchmark_search(self, server: FhirServer):
        query_results = {}
        for query in self.queries:
            print(f"Running query: {query.to_query_string()} {self.n_attempts} times")
            query_attempts = []
            for attempt in range(self.n_attempts):
                start_time = time.perf_counter()
                result = server.query(query_parameters=query).all()
                print(f"Attempt {attempt} returned {result.total} results")
                elapsed_time = time.perf_counter() - start_time
                query_attempts.append(elapsed_time)
            query_results[query.to_query_string()] = query_attempts

        self._results.add_result(
            BenchmarkOperations.QUERY,
            server.api_address,
            results=query_results,
        )

    def _benchmark_update_single(self, server: FhirServer):
        pass

    def _benchmark_batch_update(self, server: FhirServer):
        pass
