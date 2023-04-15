Querying a FHIR server a FHIR server for resources is done using the `query()` method of the `FhirServer` class.
As with all methods of the `FhirServer` class, the `query()` method can be used in both synchronous and asynchronous (`query_async`)
modes.

## Quick start
Use the `query()` (or `query_async()`) method with the name of the resource to query a FHIR server for the resources of that type.
This will return a `Query` object which can be used to further refine the query and execute it against the server.


```python
from fhir_kindling import FhirServer

# Initialize the client and query instance with a string defining the name of the resource
server = FhirServer(api_address="http://fhirtest.uhn.ca/R4")
query = server.query(resource="Patient")
# optionally add conditions by which to filter the requested resources
query = query.where({"active": True})

# Finally execute the query against the server and return the query results
results = query.all()

# In asynchronous mode, the query is create using query_async and executed with the `await` keyword
async_query = server.query_async(resource="Patient")
async_results = await async_query.all()
```

## Building a query
This section will walk you through the different ways of creating and modifying a query using the kindling library.

!!! note
    Remember to use the `query_async()` method in an asynchronous context. Everything else works exactly the same.

### Ways to define a query
Fhir kindling supports three ways of defining a query:

- [iteratively building the query](#specify-base-resource) by starting with base resource and using the 
  `query(resource=xxx)`, `where()`, `include()` and `has()` methods
- [passing an existing FHIR REST API query string](#passing-an-existing-query-string) to the `query(query_string=xxx)` method as a string
- [passing FhirQueryParameters](#passing-fhirqueryparameters) to the `query(query_parameters=xxxx)` method

#### Specify base resource
The resource to be queried can be specified using the `resource` parameter of the `query()` method. This parameter can be
either a string or a pydantic model from the [fhir.resources](https://github.com/nazrulworld/fhir.resources) library.

```python
from fhir_kindling import FhirServer
from fhir.resources.patient import Patient

server = FhirServer(url="http://fhirtest.uhn.ca/R4")
# the resource can be specified as a string
query = server.query(resource="Patient")
# or as a pydantic model
query = server.query(resource=Patient)
```

#### Passing an existing query string
An existing query string can be passed to the `query()` method using the `query_string` parameter. The query string should be a
valid FHIR REST API query string i.e. `/Patient?birthDate=gt2000`. For more information on how to construct a query string, see the 
[FHIR search specification](https://www.hl7.org/fhir/search.html). And will be parsed into a `FhirQueryParameters` object.

```python   
from fhir_kindling import FhirServer

server = FhirServer(url="http://fhirtest.uhn.ca/R4")
query = server.query(query_string="/Patient?birthDate=gt2000")
```

#### Passing FhirQueryParameters

A `FhirQueryParameters` object can be passed to the `query()` method using the `query_parameters` parameter. This object can be
constructed manually or by using the `FhirQueryParameters.from_query_string()` method.

```python
from fhir_kindling import FhirServer
from fhir_kindling.fhir_query import FhirQueryParameters

server = FhirServer(url="http://fhirtest.uhn.ca/R4")
# construct the query parameters manually
query_parameters = FhirQueryParameters(resource="Patient")
query = server.query(query_parameters=query_parameters)
```

### Add conditions to a query
FHIR queries can be further refined by adding conditions to the query. These conditions are specified using the `where()` method and are 
evaluated against the fields of the main resource. For detailed documentation on how FHIR Search works, see the 
[FHIR search specification](https://www.hl7.org/fhir/search.html).
Conditions can be added in two ways:

- Using the arguments of the `where()` method: `where(field=value1, operator=gt, value=value2)`
- Passing `FieldParameter` as an object or a dictionary to the `where()` method: `where(field_param=FieldParameter(...))`

```python
# server and query initialized the same way as in the previous examples
from fhir_kindling.fhir_query import FieldParameter

# three ways of adding filter conditions
# adding filter conditions using kv arguments
query = query.where(field="birthDate", operator="gt", value="1990")
# or using a FieldParameter object
param = FieldParameter(field="birthDate", operator="gt", value="1990")
query = query.where(field_param=param)
# or using a dictionary
param_dict = {"field": "birthDate", "operator": "gt", "value": "1990"}
query = query.where(field_param=param_dict)
```
!!! note
    To see the current state of the query check either the `query_string` or `query_parameters` attributes of the `FhirQuery` object.


### Include related resources
Related resources can be included in the response by using the `include()` method. For more information on how relations
work in the FHIR specification, see the [FHIR search specification](https://www.hl7.org/fhir/search.html#include).

Regular include i.e. include `Condition` resources related to the `Patient` resource:
```python
# server initialized the same way as in the previous examples
query = server.query(resource="Patient")
query = query.include(resource="Condition", reference_param="subject")
```

An example for reverse include would be to include the `Organization` resource related to the `Patient` resource.
I.e. like this:
```python
# server initialized the same way as in the previous examples

query = server.query(resource="Patient")
query = query.include(resource="Organization", reference_param="managingOrganization", reverse=True)
```

### Filter based on related resources
To filter based on related resources, the `has()` method can be used. This could mean for example querying only for 
patients that have a specific Condition. For more information on how this works, see the
[FHIR search specification](https://www.hl7.org/fhir/search.html#has). 
Once again this method can be used in two ways:

- Using the arguments of the `has()` method: `has(resource=xxx, reference_param=yyy, search_param=zzz, operator=eq, value=aaa)`
- Passing `ReverseChainParameter` as an object or a dictionary to the `has()` method: `has(has_param=HasParameter(...))`

```python
# server + query initialized the same way as in the previous examples
from fhir_kindling.fhir_query import ReverseChainParameter
# using kv arguments
query = query.has(resource="Condition", reference_param="subject", search_param="code", operator="eq", value="123")

# using a ReverseChainParameter object
param = ReverseChainParameter(resource="Condition", reference_param="subject", search_param="code", operator="eq", value="123")
query = query.has(has_param=param)

```

## Executing the query

!!! note
    Remember to add the `await` keyword when the query was created using the `query_async()` method.


The query is executed against the server using on of the following methods:

- `all()` - returns all resources matching the query
- `first()` - returns the first resource matching the query
- `limit(n=k)` - returns the first `k` resources matching the query
- `count()` - returns the number of resources matching the query

```python
# query initialized the same way as in the previous examples

# get all resources matching the query
response = query.all()
# In asynchronous mode, the query is create using query_async and executed with the `await` keyword
response = await query.all()

# limit the number of returned resources
response = query.limit(n=10)
# get the first resource
response = query.first()
# count the number of resources matching the query
response = query.count()
```

## Working with the response
If the query succeeded, the response will a `QueryResponse` object. This object contains the following attributes:

- `status_code` - the status code of the response
- `resources` - a list of resources of the main resource type matching the query
- `included_resources` - If the query was configured to include related resources, these are returned in this 
   attribute. List of object containing included resources separated by resource type.
- `total` - the total number of resources matching the query

```python
# query initialized the same way as in the previous examples

# get all resources matching the query
response = query.all()
print(response.status_code)
print(response.resources)
print(response.included_resources)

```


### Saving the response to a file
The response can be saved to disk as a bundle using the `save()` method. The method accepts the following parameters:

- `file_path` - the path to the file to save the response to
- `output_format` - the format to save the response in. Can be either `json` or `xml`. Default is `json`

```python
# query initialized the same way as in the previous examples
response = query.all()
# save the response to a file
response.save(file_path="response.json")
# save the response to a file in xml format
response.save(file_path="response.xml", output_format="xml")
```

## Get resources by reference
Resources can be retrieved by their reference using the `get()` and `get_many()` methods. Given a reference or a list
of references, the method will return the corresponding resource or list of resources.

Getting a single resource:
```python
# server initialized the same way as in the previous examples

# a single reference
patient_ref = "Patient/123"
# returns a single resource
patient = server.get(patient_ref)

# get many resources
patient_refs = ["Patient/123", "Patient/456"]
# returns a list of resources
patients = server.get_many(patient_refs)
```


## Query API

::: fhir_kindling.fhir_server.fhir_server.FhirServer
    handler: python
    rendering:
      members: True
      show_source: False
      heading_level: 3
    options:
      members:
        - query
        - query_async
        - get
        - get_many

