Deleting resources from the server can be achieved with the `delete()` and `delete_async()` methods of the `FhirServer`
class. 

These methods accept either a list of references in the format `[ResourceType]/[id]` or a list of `fhir.resources` objects
that are required to have a server assigned `id` and `resource_type` attribute.

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