## Query CLI
The CLI allows for querying a server either based on an already exisiting query string or by specifying a resource that
you would like to query.
The results can optionally be stored either as a raw bundle response or as a flattened csv file.

In a shell with `fhir_kindling` installed in python (activated venv)
```shell
fhir_kindling query --help
```

With auth information for stored in environment variable `FHIR_TOKEN`, this command will query for all observations and
store them in a csv file under a given name.
```shell
fhir_kindling query -r Observation --url https://blaze-fhir.personalhealthtrain.de/fhir -f query_result.csv -o csv
```
Execute a query string against a given server
```shell
fhir_kindling query -q "/MolecularSequence?patient.organization.name=DEMO_HIV&_format=json" --url <base-url-fhir-api> -u <username> -p <password> --token <token> -f "query_results.csv" -o csv
```

## Query API

::: fhir_kindling.fhir_query.query_server
    rendering:
      heading_level: 3
      show_root_heading: True
      show_root_full_path: False

::: fhir_kindling.fhir_query.query_resource
    rendering:
      heading_level: 3
      show_root_heading: True
      show_root_full_path: False

::: fhir_kindling.fhir_query.query_with_string
    rendering:
      heading_level: 3
      show_root_heading: True
      show_root_full_path: False
