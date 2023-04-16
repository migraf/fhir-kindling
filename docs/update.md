Updating resource on the server is done with the `update()` and `update_async()` methods of the `FhirServer` class.
These methods accept a list of `fhir.resources` objects that are required to have a server assigned `id` and `resource_type` attribute.
These resources are then updated on the server using a batch transaction.

!!! note
    As with all the methods of the library, there are asynchronous and synchronous versions of the methods presented here.
    Simply add the `await` keyword and append `_async` to the method name to use the asynchronous version.

```python
from fhir_kindling import FhirServer
from fhir.resources.patient import Patient

fhir_server = FhirServer(api_address="http://fhir.example.com/R4")
# Get a list of 100 patients
patients = server.query("Patient").limit(100).resources

# Update the first name of all patients
for patient in patients:
    patient.name[0].given[0] = "John"

# Update the patients on the server
update_response = fhir_server.update(resources=patients)
print(update_response)
```

## Update API

::: fhir_kindling.fhir_server.fhir_server.FhirServer
    handler: python
    rendering:
      members: True
      show_source: False
      heading_level: 3
    options:
      members:
        - update
        - update_async



