---
title: NAV TITLE 
---
#

<style>
.heading {
    font-size: 4em;
    font-weight: bold;
    margin: 0;
    padding: 0;
    text-align: center;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
}

</style>
<div class="heading">
<img src="logo/kindling_header.png" alt="logo">
</div>
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
Datascience features include flattening of resources and bundles into tabular format (pandas dataframe) and plotting 
methods for resources and bundles can optionally be included with the `ds` extra.

!!!warning 
    Under construction. This documentation is not complete.

## Features
- Connect to FHIR (Version R4) servers using different auth methods
- Sync/async CRUD operations for bundles and resource
- Resource transfer between servers
- Resource/Bundle serialization to CSV
- Resource generation for synthetic data sets

## Installation

To install the package via pypi without any extra dependencies, use the following command:
```shell
pip install fhir_kindling
```

```shell
poetry add fhir_kindling
```

### Extras (optional)
Fhir kindling can be used with the following extras:
#### Data science
Install the package with the `ds` extra to get the following features:

- `flatten` method for flattening a resource into a tabular format (pandas dataframe)
- `flatten_bundle` method for flattening a bundle into a tabular format (pandas dataframe)
- [Plotly](https://plotly.com/python/) based plotting methods for resources and bundles

```shell
pip install fhir_kindling[ds]
```


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
package.

