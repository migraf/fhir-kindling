![Header](./docs/logo/kindling_header.png)

[![CI](https://github.com/migraf/fhir-kindling/actions/workflows/main_ci.yml/badge.svg?branch=main)](https://github.com/migraf/fhir-kindling/actions/workflows/main_ci.yml)
[![codecov](https://codecov.io/gh/migraf/fhir-kindling/branch/main/graph/badge.svg?token=FKQENFXACB)](https://codecov.io/gh/migraf/fhir-kindling)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintainability](https://api.codeclimate.com/v1/badges/3b83aa52724b6e75fc22/maintainability)](https://codeclimate.com/github/migraf/fhir-kindling/maintainability)
![PyPI - Downloads](https://img.shields.io/pypi/dm/fhir_kindling)
![PyPI](https://img.shields.io/pypi/v/fhir_kindling)



Python library for interacting with [HL7 FHIR](http://hl7.org/fhir/) servers and resources. Resource validation and parsing powered by
[pydantic](https://github.com/samuelcolvin/pydantic) and the [fhir.resources](https://github.com/nazrulworld/fhir.resources) library.
Provides a simple interface for synchronous and asynchronous CRUD operations for resources and bundles, 
as well as resource transfer between servers.
Datascience features include flattening of resources and bundles into tabular format (pandas dataframes) and plotting 
methods for resources and bundles can optionally be included with the `ds` extra.

Check out the [documentation](https://migraf.github.io/fhir-kindling/) for more information and a detailed user guide.


Table of Contents
=================

- [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
    - [Extras (optional)](#extras-optional)
  - [Usage](#usage)
    - [Connecting to a FHIR server](#connecting-to-a-fhir-server)
    - [Query resources from the server](#query-resources-from-the-server)
      - [Basic resource query](#basic-resource-query)
      - [Query with filters](#query-with-filters)
      - [Including related resources in the query](#including-related-resources-in-the-query)
      - [Query resources by reference](#query-resources-by-reference)
    - [Add resources to the server](#add-resources-to-the-server)
    - [Deleting/Updating resources](#deletingupdating-resources)
    - [Transfer resources between servers](#transfer-resources-between-servers)
  - [Performance](#performance)
  - [Contributing](#contributing)
    - [Development](#development)
    - [Tests](#tests)
  - [Credits](#credits)

## Features

- Create, Read, Update, Delete resources using a FHIR server's REST API
- Transfer resources between servers while maintaining referential integrity using server-given IDs
- Bundle creation, validation and data management on a FHIR server via the REST API
- Supports Hapi, Blaze and IBM FHIR servers
- CSV serialization of query results
- Synthetic data generation and



<!-- Created by https://github.com/ekalinin/github-markdown-toc -->


## Installation

Install the package using pip:

```shell
pip install fhir-kindling --user
```

### Extras (optional)
Fhir kindling can be used with the following extras:
- `ds` for data science related features, such as flattening of resources into a tabular format

```
pip install fhir-kindling[ds] --user
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

#### Query resources by reference

If you know the id and resource type of the resource you want to query, you can use the `get` method for a single
reference
for a list of references use `get_many`. The passed references should follow the format of `<resource_type>/<id>`.

```python
# server initialization omitted
patient = server.get("Patient/123")

patients = server.get_many(["Patient/123", "Patient/456"])

```

### Add resources to the server

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

### Deleting/Updating resources

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

### Transfer resources between servers

Transferring resources between servers is done using the `transfer` method on the server object. Using this method
server assigned ids are used for transfer and referential integrity is maintained.  
This method will also attempt to get all the resources that are referenced by the resources being transferred from the
origin
server and transfer them to the destination server as well.

```python
from fhir_kindling import FhirServer

# initialize the two servers
server_1 = FhirServer(api_address="https://fhir.server/fhir")
server_2 = FhirServer(api_address="https://fhir.server/fhir")

# query some resources from server 1
conditions = server_1.query("Condition").limit(10)
# transfer the resources to server 2
response = server_1.transfer(server_2, resources=conditions.resources)

```

## Performance

This library performs request at least 1.5 times faster than other popular python FHIR libraries.
See [Benchmarks](benchmarks/README.md) for a more detailed description of the benchmarks.
![Query Results](benchmarks/results/query_plot.png)


## Contributing
Contributions are very welcome and greatly appreciated! If you want to contribute to this project, please fork the 
repository and make changes as you'd like. Pull requests are warmly welcome and credit will always be given.

### Development

To set up your environment to develop this package make sure you have [poetry](https://python-poetry.org/) installed and
run the following commands:

Install the dependencies:
```bash
poetry install --with dev --all-extras
```

Install pre-commit hooks:

- Linting: [ruff](https://github.com/charliermarsh/ruff)
- Formatting [black](https://black.readthedocs.io/en/stable/)

```bash
poetry run pre-commit install
```

### Tests
To run the full test suit you need access to two FHIR servers (the second one is used for transfer tests).
You can spin up two servers (one HAPI and one Blaze FHIR) using the compose file in the `testing` directory.
```bash
cd testing
docker compose up
```
The servers will be available at `http://localhost:9090/fhir` and `http://localhost:9091/fhir` respectively.
And the test should be configured to use them via the environment variables `FHIR_API_URL` and `TRANSFER_SERVER_URL` respectively.

Run the tests:
```bash
poetry run pytest
```


## Credits

This package was created with Cookiecutter and
the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter) project template.





