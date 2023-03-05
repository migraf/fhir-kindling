## Upload data to a fhir server
Using this library resources can be added to a fhir server as single resources, lists or as predefined 
bundles.


### Uploading a single resource

Uploading a single resource is done by calling the `add` function on a FHIR server.
The response contains the resource including the server defined id of the resource.  
The add function takes as argument either a dictionary containing the definition of a resource or a 
pydantic model object of the resource.

#### Pydantic model

```python
from fhir_kindling import FhirServer
from fhir.resources.patient import Patient

patient = Patient(
    name=[
        {
            "family": "Smith",
            "given": ["John"],
        },
    ],
    birthdate="1955-05-05"
)

fhir_server = FhirServer(api_address="http://fhir.example.com/R4")
response = fhir_server.add(resource=patient)
```

To upload an existing bundle to a FHIR server use the upload command of the cli, or the top level upload module


## Transferring data between FHIR servers






