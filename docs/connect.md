This page will showcase the different options to connect to the REST API of any FHIR server.
In the simplest case (which is not recommended), you can connect to an unsecured REST API by intializing
a server object with only base URL.

```python
from fhir_kindling import FhirServer

fhir_server = FhirServer(api_address="http://fhir.example.com/R4")
```


## Connecting with basic auth
To use basic auth, you need to provide the username and password.

```python
from fhir_kindling import FhirServer

fhir_server = FhirServer(api_address="http://fhir.example.com/R4", username="my_username", password="my_password")
```

## Connecting using a static token
Use a static token to connect to the FHIR server.

```python
from fhir_kindling import FhirServer

fhir_server = FhirServer(api_address="http://fhir.example.com/R4", token="my_token")
```

## Connect using OpenID Connect
To use OpenID Connect, you need to provide the client id and client secret, as well as the URL to the OpenID Connect server.

```python
from fhir_kindling import FhirServer

fhir_server = FhirServer("https://fhir.server/fhir", client_id="client_id", client_secret="secret",
                         oidc_provider_url="url")
```


## Initialization via environment variables
A connection to the server can be initialized based on environment variables. The keys for the environment
variables corresponding to the above described authentication methods are the following:

- Basic Auth:
    - `FHIR_USER`
    - `FHIR_PW`
- Static Token:
    - `FHIR_TOKEN`
- OIDC:
    - `CLIENT_ID`
    - `CLIENT_SECRET`
    - `OIDC_PROVIDER_URL`

!!! note
    Make sure only one of the options is present in the environment. Otherwise, the connection will fail.

```python
from fhir_kindling import FhirServer

fhir_server = FhirServer.from_env()
```

## Advanced connection options

### Headers & Proxies

Additional headers can be added to the request by setting the `headers` parameter when initializing the server object.
The `proxies` parameter can be used to set proxies for the requests.

```python
from fhir_kindling import FhirServer

fhir_server = FhirServer(api_address="http://fhir.example.com/R4", headers={"X-My-Header": "my_value"},
                         proxies={"http": "http://proxy.example.com:8080"})
```


### Retrying request

By default all requests against a FHIR server that fail will raise an exception. This can be changed by setting either the
`retry_status_codes` or `retryable_methods` when initializing the server object. The `retry_status_codes` is a list of
status codes that should be retried. The `retryable_methods` is a list of HTTP methods that should be retried.

```python
from fhir_kindling import FhirServer

fhir_server = FhirServer(api_address="http://fhir.example.com/R4", retry_status_codes=[500, 502, 503, 504])
```

#### Retry configuration

The default retry configuration is to retry 5 times with an exponential backoff. This can be changed by setting additional configuration
parameters when initializing the server object. Read more about backoff and jitter [here](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/).

```python
from fhir_kindling import FhirServer

fhir_server = FhirServer(api_address="http://fhir.example.com/R4", retry_status_codes=[500, 502, 503, 504],
                         retry_backoff_factor=0.5, retry_max_retries=10, max_backoff_wait=60)
```




