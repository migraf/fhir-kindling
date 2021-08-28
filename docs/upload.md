## Uploading a bundle

To upload an existing bundle to a FHIR server use the upload command of the cli, or the top level upload module


### CLI

View the configuration options for the upload command by executing `fhir_kindling upload --help`.
To upload a json bundle specify its path (or the path to a directory containing multiple bundles).
```terminal
fhir_kindling upload <path-to-bundle> [options]
```

#### Specifying the FHIR server and credentials

- `--url` specifies the base endpoint of the REST api of the FHIR server to upload to
- `-u`/`--username` username to use in Basicauth authentication for the server
- `-p`/`--password` password for Basicauth
- `-t`/`--token` token to be used as Bearer token for token based authentication (keycloak, OIDC)




## API docs

::: fhir_kindling.upload


