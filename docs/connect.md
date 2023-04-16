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




