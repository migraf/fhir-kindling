## Benchmarks

Comparing the library's performance with the other most popular client libraries `fhirpy` and `fhirclient`.
Perform the benchmarks by running `python benchmarks/benchmark.py`

### Environment

All operations were performed against a [Blaze](https://github.com/samply/blaze) server version `0.17.12` running in a
docker container on a 64-bit Windows 11 machine.

### Query Benchmark

When querying `n=10000` patients from the server the following results were observed. FHIR kindling executed the sync
query at least twice as fast as the other client libraries. Comparisons for the async versions will follow.

![Query Results](results/query_plot.png)
