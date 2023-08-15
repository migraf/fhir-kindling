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


@pytest.fixture
def benchmark_result(server) -> BenchmarkResult:
    transfer_server = FhirServer(api_address=os.getenv("TRANSFER_SERVER_URL"))
    benchmark = ServerBenchmark(
        servers=[server, transfer_server],
        server_names=["blaze", "hapi"],
        n_attempts=2,
        dataset_size=10,
    )

    benchmark_result = benchmark.run_suite(progress=False, save=False)

    return benchmark_result


def test_benchmark(server):
    transfer_server = FhirServer(api_address=os.getenv("TRANSFER_SERVER_URL"))
    benchmark = ServerBenchmark(
        servers=[server, transfer_server],
        server_names=["blaze", "hapi"],
        n_attempts=3,
        dataset_size=10,
    )

    # TODO remove

    # create a temporary directory to store the benchmark results
    with tempfile.TemporaryDirectory() as tmpdirname:
        benchmark.run_suite(progress=False, save=True, results_dir=tmpdirname)

        # check that two files were created
        assert len(os.listdir(tmpdirname)) == 2


def test_benchmark_result_save_load(benchmark_result):
    with tempfile.TemporaryDirectory() as tmpdirname:
        benchmark_file = os.path.join(tmpdirname, "benchmark_result.json")
        benchmark_result.save(benchmark_file)

        benchmark_result_loaded = BenchmarkResult.load(benchmark_file)

        assert benchmark_result == benchmark_result_loaded

    benchmark_result.save("benchmark_result.json")


def test_benchmark_figures(benchmark_result):
    figure = benchmark_result.plot_results()
    assert figure is not None

    figure.show()
