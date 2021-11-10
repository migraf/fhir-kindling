## Query Resources
The most basic building block of a FHIR query is the resource being queried. That's why the entrypoint to querying a
FHIR server, is specifying the resource to query for.  
After connecting to a FHIR server the API can be queried in a number of ways.

### Simple example
After initializing the client, you can query the server for a list of all the patients in the system.  

```python
from fhir_kindling import FhirServer

# Initialize the client and query instance with a string defining the name of the resource
server = FhirServer(url="http://fhirtest.uhn.ca/R4")
query = server.query(resource="Patient")
# optionally add conditions by which to filter the requested resources
query = query.where({"active": True})

# Finally execute the query against the server and return the query results
results = query.all()

```

### Query using pydantic resource
The resource to be queried can also be specified using a pydantic model from the fhir.resources library.  

```python
from fhir_kindling import FhirServer
from fhir.resources.patient import Patient

server = FhirServer(url="http://fhirtest.uhn.ca/R4")
query = server.query(resource=Patient)

query_result = query.all()
```



## Query CLI
The CLI allows for querying a server either based on an already existing query string or by specifying a resource that
you would like to query.
The results can optionally be stored either as a raw bundle response or as a flattened csv file.

In a shell with `fhir_kindling` installed in python (activated venv)
```shell
fhir_kindling query --help
```

With auth information for stored in environment variable `FHIR_TOKEN`, this command will query for all observations and
store them in a csv file under a given name.
```shell
fhir_kindling query -r Observation --url https://blaze-fhir.personalhealthtrain.de/fhir -f query_result.csv -o csv
```
Execute a query string against a given server
```shell
fhir_kindling query -q "/MolecularSequence?patient.organization.name=DEMO_HIV&_format=json" --url <base-url-fhir-api> -u <username> -p <password> --token <token> -f "query_results.csv" -o csv
```
