# :fire: FHIR Kindling

CRUD library for fhir servers, with resource validation and parsing powered by
[pydantic](https://github.com/samuelcolvin/pydantic)
models created in the [fhir.resources](https://github.com/nazrulworld/fhir.resources) library.

!!!warning 
    Under construction. This documentation is not complete.

## Features
- Connect to FHIR (Version R4) servers using different auth methods
- CRUD operations
- Bundle upload, download and transfer
- Resource validation
- Resource generation for synthetic data sets

## Installation

### Install via pypi

```shell
pip install fhir_kindling
```

### Install from source

```shell
git clone https://github.com/migraf/fhir-kindling.git
cd fhir_kindling
pip install .
```

The `fhir kindling` command should now be available in your shell (with the venv enabled) test it with
`fhir_kindling --help`

## Quick start

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

All the FHIR resource validation is done via the [fhir.resources](https://github.com/nazrulworld/fhir.resources)
package. The CLI was built using [click](https://click.palletsprojects.com/en/8.0.x/). This package was created with
Cookiecutter and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter) project template.
