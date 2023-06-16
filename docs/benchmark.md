# Benchmarking

Fhir kindling provides tooling to run reproducible benchmarks against FHIR servers.
The benchmark cover common CRUD operations as well as FHIR search requests with increasing complexities.
To perform these tests the benchmarking tool creates a synthetic dataset with configurable size that is used to populate the server.
The benchmarking tool then performs the operations against the server and records the time it took to complete each operation.
Dataset size and the number of attempts made for each step in the benchmark can be configured.

After the benchmark is successfully run the the results are stored as a JSON file and also plotted as a graph and saved as a PNG file.


## Prerequisites
- [Docker](https://docs.docker.com/get-docker/)(for preconfigured benchmarks)
- Fhir kindling installed

## Run preconfigured benchmarks
To easily test how the most common fhir implementations perform on your machine you can use the preconfigured benchmarks.

First clone the repository on the machine you want to run the benchmarks on.
```bash
git clone https://github.com/migraf/fhir-kindling.git
```
The `benchmarks` directory contains a `docker-compose.yml` file that starts a Blaze, HAPI, and Linux4Health FHIR server.
Start the servers using docker compose
```bash
docker compose up -d
```

If not already installed, install the `fhir_kindling` with the ds extras
```bash
pip install fhir_kindling[ds] --pre
```

Or install using poetry (recommended) in the root directory of the repository
```bash
poetry install --extras ds
```

These servers are configured by default in the `benchmark_servers.py` script. If you want to add your own server, you can do so by adding it to the `servers` list in the script.

Run the benchmark script
```bash
python benchmark_servers.py
```

## Configuring the benchmark
There are multiple configuration options to adapt the benchmark to your needs.

- You can modify the number of resources and attempts the benchmark makes.
- You can select which steps to run in case you dont want to run the full suite
- You can add your own custom search queries to be evaluated against the servers

### Size and number of attempts
Modify the dataset size and the number of attempts made for each step in the benchmark by settings the `dataset_size` and `n_attempts` variables on the `ServerBenchmark` instance. (Keep in mind that the dataset size changes with approximately a factor of 10 based on the parameter given in the `dataset_size` variable.)

```python
from fhir_kindling import FhirServer
from fhir_kindling.benchmark import ServerBenchmark

servers = [FhirServer(api_adress="http://localhost:9090/fhir")")]
benchmark = ServerBenchmark(
    servers=servers,
    dataset_size=1000,
    n_attempts=3,
)

```


### Steps and custom queries
By passing a list of steps (`generate`, `query`, `insert`, `dataset_insert`, `update`, `delete`) to the `steps` parameter you can select which steps to run in the benchmark.
You can run your own queries by passing either FHIR REST query strings or `FhirQueryParameter` objects to the `custom_queries` parameter.

```python
from fhir_kindling import FhirServer
from fhir_kindling.benchmark import ServerBenchmark

servers = [FhirServer(api_adress="http://localhost:9090/fhir")")]
benchmark = ServerBenchmark(
    servers=servers,
    steps=["generate", "dataset_insert", "query"],
    custom_queries=["Condition?_count=1000", "Observation?_count=10000"],
)

```

## API Reference

::: fhir_kindling.benchmark.bench.ServerBenchmark
    handler: python
    rendering:
      members: True
      show_source: False
      heading_level: 3















