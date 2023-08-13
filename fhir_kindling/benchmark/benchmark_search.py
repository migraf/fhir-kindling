import time
from typing import TYPE_CHECKING

from fhir_kindling import FhirServer
from fhir_kindling.benchmark.results import SearchOperationResult, SearchQueryResult
from fhir_kindling.util.date_utils import local_now

if TYPE_CHECKING:
    from fhir_kindling.benchmark.bench import ServerBenchmark


def benchmark_search(
    benchmark: "ServerBenchmark",
    server: FhirServer,
) -> SearchOperationResult:
    search_result = SearchOperationResult()

    query_results = []

    for name, query in benchmark.queries:
        query_attempts = []
        count = 0
        for _ in range(benchmark.n_attempts):
            start_time = time.perf_counter()
            response = server.query(query_parameters=query).all()
            count = response.total
            elapsed_time = time.perf_counter() - start_time
            query_attempts.append(elapsed_time)

        query_result = SearchQueryResult(
            name=name,
            query_string=query.to_query_string(),
            result_count=count,
            attempts=query_attempts,
        )
        query_results.append(query_result)

    search_result.query_results = query_results
    search_result.end_time = local_now()
    search_result.success = True
    search_result.duration = (
        search_result.end_time - search_result.start_time
    ).total_seconds()

    return search_result
