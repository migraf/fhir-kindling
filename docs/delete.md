Deleting resources from the server can be achieved with the `delete()` and `delete_async()` methods of the `FhirServer`
class. 

These methods accept either a list of references in the format `[ResourceType]/[id]` or a list of `fhir.resources` objects
that are required to have a server assigned `id` and `resource_type` attribute.

!!! note
    As with all the methods of the library, there are asynchronous and synchronous versions of the methods presented here.
    Simply add the `await` keyword and append `_async` to the method name to use the asynchronous version.

```python
from fhir_kindling import FhirServer
from fhir.resources.patient import Patient

fhir_server = FhirServer(api_address="http://fhir.example.com/R4")

# delete by list of references
delete_list = ["Patient/123", "Patient/456", "Patient/789"]
fhir_server.delete(references=delete_list)

# delete resources by list of fhir.resources objects
patient = Patient(id="123", resource_type="Patient")
fhir_server.delete(resources=[patient])

```

## Delete API

::: fhir_kindling.fhir_server.fhir_server.FhirServer
    handler: python
    rendering:
      members: True
      show_source: False
      heading_level: 3
    options:
      members:
        - delete
        - delete_async