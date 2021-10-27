[![codecov](https://codecov.io/gh/migraf/fhir-kindling/branch/master/graph/badge.svg?token=FKQENFXACB)](https://codecov.io/gh/migraf/fhir-kindling)
[![Pipeline](https://github.com/migraf/fhir-kindling/actions/workflows/github_actions.yml/badge.svg)](https://github.com/migraf/fhir-kindling/actions/workflows/github_actions.yml)
[![PyPI version](https://badge.fury.io/py/fhir-kindling.svg)](https://badge.fury.io/py/fhir-kindling)
# FHIR Kindling
Synthetic FHIR resource generator and FHIR server data management tool. [Documentation](https://migraf.github.io/fhir-kindling/)

## Features
- CLI for step by step data set/FHIR resource creation
- Bundle creation, validation and data management on a FHIR server via the REST API
- Supports Hapi, Blaze and IBM FHIR servers



## Installation
In a virtual environment clone the project and install it using pip:
```shell
cd fhir_kindling
pip install .
```
The `fhir_kindling` command should now be available in your shell (with the venv activated) test it with
`fhir_kindling --help`

## Usage
With the virtual environment activated you can use the CLI directly in the terminal directly

### CLI - Uploading a bundle to a server
```shell
fhir_kindling upload <path-to-bundle.json> --url <base-url-fhir-api> -u <username> -p <password> --token <token>
```

### CLI - Querying a server
For an overview of the options of the CLI query command
```shell
fhir_kindling query --help
```

#### Examples
To query all instances of a resource use the `-r` option. This command queries all Patients from the server and stores
the results as csv into the `query_results.json` file.
```shell
fhir_kindling query -r Patient --url <base-url-fhir-api> -u <username> -p <password> --token <token> -f "query_results.csv" -o csv
```

This example uses the `-q` option to execute a predefined url query string against the server and also stores the output
as csv in a file called `query_results.csv`

```shell
fhir_kindling query -q "/MolecularSequence?patient.organization.name=DEMO_HIV&_format=json" --url <base-url-fhir-api> -u <username> -p <password> --token <token> -f "query_results.csv" -o csv
```



## Credits
This package was created with Cookiecutter and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter) project template.





