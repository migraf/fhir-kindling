Transfering resources between different fhir servers was the original reason for the creation of this library. In the FHIR format this poses significant challenges as referential integrity is strictly enforced and batched transaction do not autmatically resolve the order of object creation and server generate id assignment. 

To solve this problem the `FhirServer` class has a `transfer()` method that can be used to transfer resources from one server to another. This method accepts either a list of `fhir.resources` objects that are required to have a server assigned `id` and `resource_type` attribute or a `FhirQuery` object whose results should be transfered. Additionally, the `transfer()` method accepts a `target_server` argument that is a `FhirServer` object that represents the server to which the resources should be transfered.

In the default configuration the provided resources (either the list or the results of the executed query) are then analyzed for missing references. If any are found, the `FhirServer` will attempt to resolve them by querying the source server for the missing resources. If the missing resources are found, a DAG is created that represents the order in which the resources should be created on the target server. This DAG is then used to create the resources on the target server in the correct order keeping the referential integrity intact.

## Record Linkage

The `transfer()` method also supports record linkage. In this case this means that while transfering the newly created reference for the transfered resource will be stored in a dictionary with the hashed original reference as key. This allows back linkage from the transfered data to the data in the potentially sensitive source server with out comprosing any IDs.


## Example Usage

This example will show the transfer of the first 100 conditions from one server to another. While also transfering all referenced Patient resources 

```python

from fhir_kindling import FhirServer

src_server = FhirServer(api_address="http://fhir.example.com/R4")
target_server = FhirServer(api_address="http://fhir-2.example.com/R4")

# Get a list of 100 conditions
patients = src_server.query("Conditions").limit(100).resources

# Transfer the conditions to the target server
# this will also transfer all referenced resources (Patient, Observation, etc.)
transfer_response = src_server.transfer(resources=patients, target_server=target_server)
print(transfer_response)
```


## Transfer API

::: fhir_kindling.fhir_server.fhir_server.FhirServer
    handler: python
    rendering:
      members: True
      show_source: False
      heading_level: 3
    options:
      members:
        - transfer
