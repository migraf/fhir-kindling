# Upload data to a fhir server
Using this library resources can be added to a FHIR server as single resources, lists or as predefined 
bundles by using its REST API.

!!! note
    As with all the methods of the library, there are asynchronous and synchronous versions of the methods presented here.
    Simply add `_async` to the method name to use the asynchronous version.

## Uploading a single resource

Uploading a single resource is done by calling the `add` function on a FHIR server.
The resource can be specified as a pydantic model from the `fhir.resources` package or as a dictionary.

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
patient_dict = patient.dict()

fhir_server = FhirServer(api_address="http://fhir.example.com/R4")
response = fhir_server.add(resource=patient) # identical
response = fhir_server.add(resource=patient_dict) # identical
```


## Uploading a list of resources

Uploading a list of resources is done by calling the `add_all` function on a FHIR server and passing a list of resources.
The resources can be specified as a pydantic models from the `fhir.resources` package or as a dictionaries.

When uploading a large amounts of resources, the upload will be batched into smaller transactions to avoid timeouts.
The batch size can be specified with the `batch_size` argument.
Optionally, a progress bar can be displayed by setting the `display` argument to `True`.

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
# create a list of 10000 patients
patients = [patient for _ in range(10000)]

fhir_server = FhirServer(api_address="http://fhir.example.com/R4")

# upload the list of patients and display a progress bar
response = fhir_server.add_all(resources=patients, batch_size=1000, display=True)
```


## Uploading a bundle

Uploading a bundle is done by calling the `add_bundle` function on a FHIR server and passing a bundle object to the method.
Once again, the bundle can be specified as a pydantic model from the `fhir.resources` package or as a dictionary.

```python

from fhir_kindling import FhirServer
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
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
# create a list of 10000 patients
patients = [patient for _ in range(10000)]

bundle = Bundle(
    type="transaction",
    entry=[
        BundleEntry(
            resource=patient,
            request=BundleEntryRequest(
                method="POST",
                url="Patient",
            ),
        )
        for patient in patients
    ],
)
fhir_server = FhirServer(api_address="http://fhir.example.com/R4")

response = fhir_server.add_bundle(bundle=bundle) 

```

## Upload API

::: fhir_kindling.fhir_server.fhir_server.FhirServer
    handler: python
    rendering:
      members: True
      show_source: False
      heading_level: 3
    options:
      members:
        - add
        - add_async
        - add_all
        - add_all_async
        - add_bundle
        - add_bundle_async














