import json
import os
import time
import asyncio

from fhir_kindling.generators import PatientGenerator
from fhir_kindling import FhirServer

from fhirpy import SyncFHIRClient, AsyncFHIRClient
from fhirclient import client
import fhirclient.models.patient as p

import plotly.express as px
import pandas as pd


N = 10000


def generate_data(server_address: str, n_patients: int, results: dict):
    patient_generator = PatientGenerator(n=n_patients)

    generate_start = time.time()
    patients = patient_generator.generate()
    results["generate_time"] = time.time() - generate_start

    server = FhirServer(api_address=server_address)

    upload_start = time.time()
    server.add_all(patients)
    results["upload_time"] = time.time() - upload_start


def benchmark_sync(server_address: str, results: dict):
    # test with kindling
    server = FhirServer(api_address=server_address)
    get_all_start = time.time()
    kindling_response = server.query("Patient").limit(N)
    results["kindling_get_all_sync_time"] = time.time() - get_all_start
    print("kindling sync: ", len(kindling_response.resources))

    # test with fhirpy
    fhirpy_client = SyncFHIRClient(server_address)
    patients = fhirpy_client.resources("Patient")
    get_all_start = time.time()
    fhirpy_response = patients.limit(N).fetch()
    results["fhirpy_get_all_sync_time"] = time.time() - get_all_start
    print("fhirpy sync: ", len(fhirpy_response))

    # test with fhirclient
    settings = {
        "app_id": "blaze_app",
        "api_base": server_address,
    }
    smart_client = client.FHIRClient(settings=settings)
    get_all_start = time.time()
    smart_response = p.Patient.where(struct={"_count": "100000"}).perform_resources(
        smart_client.server
    )
    results["smart_get_all_sync_time"] = time.time() - get_all_start
    print("smart sync: ", len(smart_response))


async def benchmark_kindling_async(server_address: str, results: dict):
    # test with kindling
    server = FhirServer(api_address=server_address)
    get_all_start = time.time()
    kindling_response = await server.query_async("Patient").limit(N)
    results["kindling_get_all_async_time"] = time.time() - get_all_start
    print("kindling async: ", len(kindling_response.resources))


async def benchmark_fhirpy_async(server_address: str, results: dict):
    # test with fhirpy
    fhirpy_client = AsyncFHIRClient(server_address, authorization="Bearer TOKEN")
    patients = fhirpy_client.resources("Patient")
    get_all_start = time.time()
    patients = patients.limit(N)
    fhirpy_response = await patients.fetch()
    results["fhirpy_get_all_async_time"] = time.time() - get_all_start
    print("fhirpy async: ", len(fhirpy_response))


def plot_results(results: dict):
    results_df = pd.DataFrame(
        [
            {
                "library": "kindling",
                "time": results["kindling_get_all_sync_time"],
                "sync": "sync",
            },
            {
                "library": "kindling",
                "time": results["kindling_get_all_async_time"],
                "sync": "async",
            },
            {
                "library": "fhirpy",
                "time": results["fhirpy_get_all_sync_time"],
                "sync": "sync",
            },
            {
                "library": "fhirpy",
                "time": results.get("fhirpy_get_all_async_time"),
                "sync": "async",
            },
            {
                "library": "smart",
                "time": results["smart_get_all_sync_time"],
                "sync": "sync",
            },
            {"library": "smart", "time": None, "sync": "async"},
        ]
    )
    fig = px.bar(
        results_df,
        x="library",
        y="time",
        title="Query Patients(n=10000)",
        color="sync",
        barmode="group",
    )
    fig.update_layout(
        font_family="Courier New",
        title_font_family="Times New Roman",
        font_size=18,
    )
    fig.show()


if __name__ == "__main__":
    benchmark_server = "http://localhost:9090/fhir"

    # generate data for benchmark and measure generation and upload time

    generate_results = {}
    generate_data(benchmark_server, N, generate_results)
    with open(f"results/{N}-generate_results.json", "w") as f:
        json.dump(generate_results, f)

    # benchmark query time
    query_results = {}

    # test sync versions
    benchmark_sync(benchmark_server, query_results)

    # test async versions
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(benchmark_kindling_async(benchmark_server, query_results))
    loop.run_until_complete(benchmark_fhirpy_async(benchmark_server, query_results))
    plot_results(query_results)
    with open(f"results/query-results.json", "w") as f:
        json.dump(query_results, f)
