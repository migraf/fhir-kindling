[![codecov](https://codecov.io/gh/migraf/fhir-kindling/branch/master/graph/badge.svg?token=FKQENFXACB)](https://codecov.io/gh/migraf/fhir-kindling)
[![Pipeline](https://github.com/migraf/fhir-kindling/actions/workflows/github_actions.yml/badge.svg)](https://github.com/migraf/fhir-kindling/actions/workflows/github_actions.yml)
[![PyPI version](https://badge.fury.io/py/fhir-kindling.svg)](https://badge.fury.io/py/fhir-kindling)
# :fire: FHIR Kindling

CRUD library for fhir servers, with resource validation and parsing powered by the [pydantic](https://github.com/samuelcolvin/pydantic)
models created by [fhir.resources](https://github.com/nazrulworld/fhir.resources). 
More details in the [Documentation](https://migraf.github.io/fhir-kindling/).

## Features
- Create, Read, Update, Delete using a server's REST API
- Bundle creation, validation and data management on a FHIR server via the REST API
- Supports Hapi, Blaze and IBM FHIR servers

## Installation
Install the package using pip:
```shell
pip install fhir_kindling --user
```

## Usage

### Connecting to a FHIR server

```python
from fhir_kindling import FhirServer

# Connect with basic auth 
basic_auth_server = FhirServer("https://fhir.server/fhir", username="admin", password="admin")
# Connect with static token
token_server = FhirServer("https://fhir.server/fhir", token="your_token")

# Connect using oauth2/oidc
oidc_server = FhirServer("https://fhir.server/fhir", client_id="client_id", client_secret="secret", 
                         oidc_provider_url="url")

# Print the server's capability statement
print(basic_auth_server.capabilities)

```

### Query resources from the server
```python
from fhir_kindling import FhirServer
from fhir.resources.patient import Patient


# Connect using oauth2/oidc
oidc_server = FhirServer("https://fhir.server/fhir", client_id="client_id", client_secret="secret",
                         oidc_provider_url="url")

# query all patients on the server
query = oidc_server.query(Patient, output_format="json").all()
print(query.response)

# Query resources based on name of resource
query = oidc_server.query("Patient", output_format="json").all()
print(query.response)

```



## CLI

With the virtual environment activated you can use the CLI directly in the terminal

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





