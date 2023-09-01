import time
from typing import TYPE_CHECKING, List, Union

from tqdm import tqdm

from fhir_kindling import FhirServer
from fhir_kindling.benchmark.benchmark_search import benchmark_search
from fhir_kindling.benchmark.constants import (
    BenchmarkOperations,
)
from fhir_kindling.benchmark.results import (
    BenchmarkOperationResult,
    ServerBenchmarkResult,
)
from fhir_kindling.fhir_server.ops.transfer import (
    reference_graph,
    resolve_reference_graph,
)
from fhir_kindling.generators.patient import PatientGenerator
from fhir_kindling.util.date_utils import local_now

if TYPE_CHECKING:
    from fhir_kindling.benchmark.bench import ServerBenchmark


def run_server_benchmark(
    benchmark: "ServerBenchmark",
    server: FhirServer,
    server_name: Union[str, None],
    progress: bool = False,
) -> ServerBenchmarkResult:
    server_result = ServerBenchmarkResult(
        name=server_name,
        api_address=server.api_address,
        completed=False,
        operations=benchmark.steps,
    )
    for step in tqdm(
        benchmark.steps,
        desc=f"Server {server.api_address}",
        disable=not progress,
    ):
        if step == BenchmarkOperations.INSERT:
            server_result.single_insert = _benchmark_insert_single(benchmark, server)
        elif step == BenchmarkOperations.BATCH_INSERT:
            server_result.batch_insert = _benchmark_insert_batch(benchmark, server)
        elif step == BenchmarkOperations.DATASET_INSERT:
            server_result.dataset_insert = _upload_dataset(benchmark, server)
        elif step == BenchmarkOperations.SEARCH:
            server_result.search = benchmark_search(benchmark, server)
        elif step == BenchmarkOperations.UPDATE:
            server_result.single_update = _benchmark_update_single(benchmark, server)
        elif step == BenchmarkOperations.BATCH_UPDATE:
            server_result.batch_update = _benchmark_update_batch(benchmark, server)
        elif step == BenchmarkOperations.DELETE:
            server_result.single_delete = _benchmark_delete_single(benchmark, server)
        elif step == BenchmarkOperations.BATCH_DELETE:
            server_result.batch_delete = _benchmark_delete_batch(benchmark, server)

    server_result.completed = True
    server_result.end_time = local_now()
    server_result.duration = (
        server_result.end_time - server_result.start_time
    ).total_seconds()

    return server_result


def _benchmark_insert_single(
    benchmark: "ServerBenchmark",
    server: FhirServer,
) -> BenchmarkOperationResult:
    insert_single_result = BenchmarkOperationResult(
        operation=BenchmarkOperations.INSERT,
    )

    resources = PatientGenerator(n=benchmark.n_attempts).generate()

    timings = []
    added_resources = []
    for resource in resources:
        start_time = time.perf_counter()
        result = server.add(resource)
        added_resources.append(result.reference)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        timings.append(total_time)

    # track added resources for the server
    benchmark.add_resource_refs_for_tracking(
        server,
        added_resources,
    )

    # update the results with timings
    _update_operation_result_on_finish(
        operation_result=insert_single_result,
        attempts=timings,
    )

    return insert_single_result


def _benchmark_insert_batch(
    benchmark: "ServerBenchmark",
    server: FhirServer,
) -> BenchmarkOperationResult:
    batch_insert_result = BenchmarkOperationResult(
        operation=BenchmarkOperations.BATCH_INSERT,
    )

    generator = PatientGenerator(n=benchmark.batch_size)
    timings = []
    # run multiple attempts for inserting resources
    for _ in range(benchmark.n_attempts):
        resources = generator.generate()
        start_time = time.perf_counter()
        response = server.add_all(resources)
        elapsed_time = time.perf_counter() - start_time
        timings.append(elapsed_time)
        # track the added resources
        benchmark.add_resource_refs_for_tracking(
            server, [r.reference.reference for r in response.create_responses]
        )

    # update the results with timings
    _update_operation_result_on_finish(
        operation_result=batch_insert_result,
        attempts=timings,
    )

    return batch_insert_result


def _benchmark_delete_single(
    benchmark: "ServerBenchmark",
    server: FhirServer,
) -> BenchmarkOperationResult:
    delete_single_result = BenchmarkOperationResult(
        operation=BenchmarkOperations.DELETE,
    )
    timings = []

    # pop n_attempts generated resources from the tracking list
    server_resource_refs = benchmark.benchmark_resources.get(server.api_address, [])
    if not server_resource_refs:
        raise Exception("No resources to delete")

    for _ in range(benchmark.n_attempts):
        resource_ref = server_resource_refs.pop()
        start_time = time.perf_counter()
        server.delete(references=[resource_ref])
        elapsed_time = time.perf_counter() - start_time
        timings.append(elapsed_time)

    benchmark.benchmark_resources[server.api_address] = server_resource_refs

    # update the results with timings
    _update_operation_result_on_finish(
        operation_result=delete_single_result,
        attempts=timings,
    )

    return delete_single_result


def _benchmark_delete_batch(
    benchmark: "ServerBenchmark",
    server: FhirServer,
) -> BenchmarkOperationResult:
    delete_batch_result = BenchmarkOperationResult(
        operation=BenchmarkOperations.BATCH_DELETE,
    )

    server_resource_refs = benchmark.benchmark_resources.get(server.api_address, [])
    if not server_resource_refs:
        raise Exception("No resources to delete")

    # make batches of batch_size with the final batch being smaller
    batches = [
        server_resource_refs[i : i + benchmark.batch_size]
        for i in range(0, len(server_resource_refs), benchmark.batch_size)
    ]

    timings = []
    for batch in batches:
        server_resource_refs[: benchmark.batch_size]
        start_time = time.perf_counter()
        server.delete(references=batch)
        elapsed_time = time.perf_counter() - start_time
        timings.append(elapsed_time)

    benchmark.benchmark_resources[server.api_address] = server_resource_refs

    # update the results with timings
    _update_operation_result_on_finish(
        operation_result=delete_batch_result,
        attempts=timings,
    )

    return delete_batch_result


def _benchmark_update_single(
    benchmark: "ServerBenchmark",
    server: FhirServer,
) -> BenchmarkOperationResult:
    update_single_result = BenchmarkOperationResult(
        operation=BenchmarkOperations.UPDATE,
    )

    generator = PatientGenerator(n=benchmark.n_attempts)
    timings = []
    generated_resources = []
    for resource in generator.generate():
        server_resource = server.add(resource).resource
        generated_resources.append(server_resource.relative_path)
        # update the resource
        server_resource.birthDate = "2023-01-01"
        start_time = time.perf_counter()
        server.update([resource])
        elapsed_time = time.perf_counter() - start_time
        timings.append(elapsed_time)

    benchmark.add_resource_refs_for_tracking(
        server,
        generated_resources,
    )

    # update the results with timings
    _update_operation_result_on_finish(
        operation_result=update_single_result,
        attempts=timings,
    )

    return update_single_result


def _benchmark_update_batch(
    benchmark: "ServerBenchmark",
    server: FhirServer,
) -> BenchmarkOperationResult:
    update_batch_result = BenchmarkOperationResult(
        operation=BenchmarkOperations.BATCH_UPDATE,
    )

    generator = PatientGenerator(n=benchmark.batch_size)

    timings = []
    for _ in range(benchmark.n_attempts):
        # create resources to update
        resources = generator.generate()
        create_response = server.add_all(resources)
        server_resource_refs = [
            r.reference.reference for r in create_response.create_responses
        ]
        benchmark.add_resource_refs_for_tracking(
            server,
            server_resource_refs,
        )
        updated_resources = []
        for resource in create_response.resources:
            resource.birthDate = "2023-01-01"
            updated_resources.append(resource)

        start_time = time.perf_counter()
        server.update(updated_resources)
        elapsed_time = time.perf_counter() - start_time
        timings.append(elapsed_time)

    # update the results with timings
    _update_operation_result_on_finish(
        operation_result=update_batch_result,
        attempts=timings,
    )

    return update_batch_result


def _upload_dataset(
    benchmark: "ServerBenchmark",
    server: FhirServer,
) -> BenchmarkOperationResult:
    dataset_insert_result = BenchmarkOperationResult(
        operation=BenchmarkOperations.DATASET_INSERT,
    )

    # create temp copy of dataset
    dataset = benchmark.dataset.copy(deep=True)

    ds_graph = reference_graph(dataset.resources)
    start_time = time.perf_counter()
    added_resources, linkage = resolve_reference_graph(ds_graph, server, True, False)
    total = time.perf_counter() - start_time
    resource_refs = [r.reference.reference for r in added_resources]
    benchmark.add_resource_refs_for_tracking(server=server, refs=resource_refs)

    timings = [total]
    # update the results with timings
    _update_operation_result_on_finish(
        operation_result=dataset_insert_result,
        attempts=timings,
    )

    return dataset_insert_result


def _update_operation_result_on_finish(
    operation_result: BenchmarkOperationResult,
    attempts: List[float],
) -> None:
    """Update the operation result with the results of the benchmark."""

    operation_result.end_time = local_now()
    operation_result.attempts = attempts
    operation_result.success = True
    operation_result.duration = (
        operation_result.end_time - operation_result.start_time
    ).total_seconds()
