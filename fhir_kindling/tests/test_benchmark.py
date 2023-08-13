import os
import tempfile

import pytest
from dotenv import find_dotenv, load_dotenv

from fhir_kindling import FhirServer
from fhir_kindling.benchmark.bench import ServerBenchmark
from fhir_kindling.benchmark.results import BenchmarkResult


@pytest.fixture
def server():
    load_dotenv(find_dotenv())
    server = FhirServer(
        api_address=os.getenv("FHIR_API_URL"),
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL"),
    )
    return server


def benchmark_results(server) -> BenchmarkResult:
    transfer_server = FhirServer(api_address=os.getenv("TRANSFER_SERVER_URL"))
    ServerBenchmark(servers=[server, transfer_server], n_attempts=2, dataset_size=10)


def test_benchmark(server):
    transfer_server = FhirServer(api_address=os.getenv("TRANSFER_SERVER_URL"))
    benchmark = ServerBenchmark(
        servers=[server, transfer_server],
        server_names=["blaze", "hapi"],
        n_attempts=3,
        dataset_size=10,
    )

    # TODO remove

    results_dir = "/home/micha/projects/kindling/fhir-kindling/testing"

    # create a temporary directory to store the benchmark results
    with tempfile.TemporaryDirectory() as tmpdirname:
        benchmark.run_suite(progress=False, save=True, results_dir=results_dir)

        # check that two files were created
        assert len(os.listdir(tmpdirname)) == 2


def test_benchmark_results_load():
    results_dir = "/home/micha/projects/kindling/fhir-kindling/testing/benchmark_2023-08-13T19:15:09.720210+02:00.json"
    benchmark_result = BenchmarkResult.load(results_dir)
    assert benchmark_result
    print(benchmark_result)


def test_benchmark_figures():
    results_dir = "/home/micha/projects/kindling/fhir-kindling/testing/benchmark_2023-08-13T19:15:09.720210+02:00.json"
    benchmark_result = BenchmarkResult.load(results_dir)
    benchmark_result.plot_results()
