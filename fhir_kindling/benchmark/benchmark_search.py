from typing import TYPE_CHECKING

from fhir_kindling import FhirServer
from fhir_kindling.benchmark.results import SearchOperationResult

if TYPE_CHECKING:
    from fhir_kindling.benchmark.bench import ServerBenchmark


def benchmark_search(
    benchmark: "ServerBenchmark",
    server: FhirServer,
) -> SearchOperationResult:
    pass
