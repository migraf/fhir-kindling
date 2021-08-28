## Uploading a bundle

To upload an existing bundle to a FHIR server use the upload command of the cli, or the top level upload module


### CLI

View the configuration options for the upload command by executing `fhir_kindling upload --help`.
To upload a json bundle specify its path (or the path to a directory containing multiple bundles).
```terminal
fhir_kindling upload <path-to-bundle> [options]
```

#### Specifying the FHIR server and credentials
Select the server and authentication as command line arguments:

- `--url` specifies the base endpoint of the REST api of the FHIR server to upload to
- `-u`/`--username` username to use in Basicauth authentication for the server
- `-p`/`--password` password for Basicauth
- `-t`/`--token` token to be used as Bearer token for token based authentication (keycloak, OIDC)

If these are not present, the tool will look for authentication information under the environment variables:

- `FHIR_API_URL`
- `FHIR_USER`
- `FHIR_PW`
- `FHIR_TOKEN`

If the token option is set either via arguments or environment variables, the user and password option can not also
be set.


## API docs

::: fhir_kindling.upload


