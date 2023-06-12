from fhir_kindling import FhirServer
from fhir_kindling.benchmark import ServerBenchmark

DEFAULT_SERVERS = [
    {"name": "blaze", "api_address": "http://localhost:9090/fhir"},
    {"name": "hapi", "api_address": "http://localhost:9091/fhir"},
    {
        "name": "linux4h",
        "api_address": "http://localhost:9080/fhir-server/api/v4/",
        "credentials": {"username": "fhiruser", "password": "change-password"},
    },
]


def run_benchmark(servers=DEFAULT_SERVERS):
    """Run a benchmark against the given servers."""

    # initialize server objects
    benchmark_servers = []
    for s in servers:
        print(f"initializing Server {s['name']} -- {s['api_address']}")
        credentials = s.get("credentials", None)
        if credentials:
            benchmark_servers.append(
                FhirServer(
                    api_address=s["api_address"],
                    **credentials,
                )
            )
        else:
            benchmark_servers.append(FhirServer(api_address=s["api_address"]))

    print("running benchmark")

    benchmark = ServerBenchmark(
        servers=benchmark_servers,
        server_names=[s["name"] for s in servers],
        dataset_size=10,
        n_attempts=2,
    )
    benchmark.run_suite()
    figure = benchmark.plot()
    figure.show()


if __name__ == "__main__":
    run_benchmark()
