from fhir_kindling.benchmark.results import BenchmarkResult

RESULT_PATH = (
    "/home/micha/projects/kindling/fhir-kindling/testing/benchmark_result.json"
)


def main():
    result = BenchmarkResult.load(RESULT_PATH)
    result.timeline_plot(show=True)
    result.dataset_plot(show=True)
    result.insert_plot(show=True)
    result.update_plot(show=True)


if __name__ == "__main__":
    main()
