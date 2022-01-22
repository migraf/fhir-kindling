[![CI](https://github.com/migraf/fhir-kindling/actions/workflows/main_ci.yml/badge.svg?branch=main)](https://github.com/migraf/fhir-kindling/actions/workflows/main_ci.yml)
[![codecov](https://codecov.io/gh/migraf/fhir-kindling/branch/main/graph/badge.svg?token=FKQENFXACB)](https://codecov.io/gh/migraf/fhir-kindling)
[![PyPI version](https://badge.fury.io/py/fhir-kindling.svg)](https://badge.fury.io/py/fhir-kindling)

# :fire: FHIR Kindling

CRUD library for fhir servers, with resource validation and parsing powered by
the [pydantic](https://github.com/samuelcolvin/pydantic)
models created by [fhir.resources](https://github.com/nazrulworld/fhir.resources). More details in
the [Documentation](https://migraf.github.io/fhir-kindling/).

## Features

- Create, Read, Update, Delete using a server's REST API
- Bundle creation, validation and data management on a FHIR server via the REST API
- Supports Hapi, Blaze and IBM FHIR servers

## Installation

Install the package using pip:

```shell
pip install fhir-kindling --user
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

## Credits

This package was created with Cookiecutter and
the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter) project template.





