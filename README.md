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

#### Basic resource query

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

#### Query with filters

Filtering the targeted resource is done using the `where` method on the query object. The filter is created by defining
the target field, the comparison operator and the value to compare.

```python
from fhir_kindling import FhirServer

server = FhirServer(api_address="https://fhir.server/fhir")

query = server.query("Patient").where(field="birthDate", operator="gt", value="1980").all()
```

#### Including related resources in the query

Resources that reference or are referenced by resources targeted by the query can be included in the response using
the `include` method on the query object.

```python
# server initialization omitted
# get the patients along with the queried conditions
query_patient_condition = server.query("Condition").include(resource="Condition", reference_param="subject").all()

# get the conditions for a patient
query_patient_condition = server.query("Patient")
query_patient_condition = query_patient_condition.include(resource="Condition", reference_param="subject", reverse=True)
response = query_patient_condition.all()
```

#### Add resources to the server

Resources can be added to the server using the `add` method on the server object. Lists of resources can be added using
'add_all'.

```python
from fhir_kindling import FhirServer
from fhir.resources.patient import Patient

# Connect to the server
server = FhirServer(api_address="https://fhir.server/fhir")

# add a single resource
patient = Patient(name=[{"family": "Smith", "given": ["John"]}])
response = server.add(patient)

# add multiple resources
patients = [Patient(name=[{"family": f"Smith_{i}", "given": ["John"]}]) for i in range(10)]
response = server.add_all(patients)
```

#### Deleting/Updating resources

Resources can be deleted from the server using the `delete` method on the server object, it takes as input either
references to the resources or the resources itself.  
Similarly the `update` method can be used to update the resources on the server, by passing a list of updated resources.

```python
from fhir_kindling import FhirServer
from fhir.resources.patient import Patient

# Connect to the server
server = FhirServer(api_address="https://fhir.server/fhir")

# add some patients
patients = [Patient(name=[{"family": f"Smith_{i}", "given": ["John"]}]) for i in range(10)]
response = server.add_all(patients)

# change the name of the patients
for patient in response.resources:
    patient.name[0].given[0] = "Jane"

# update the patients on the server
updated_patients = server.update(resources=response.resources)

# delete based on reference
server.delete(references=response.references[:5])
# delete based on resources
server.delete(resources=response.resources[5:])
```

## Credits

This package was created with Cookiecutter and
the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter) project template.





