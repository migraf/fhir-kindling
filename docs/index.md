# FHIR Kindling
Synthetic FHIR resource generator and FHIR server data management tool.

!!!warning
    Under construction. This documentation is not complete.


## Features
- CLI for step by step data set/FHIR resource creation
- Bundle creation, validation and data management on a FHIR server via the REST API
- Supports Hapi, Blaze and IBM FHIR servers


## Installation
In a virtual environment clone the project and install it using pip:
```shell
cd fhir_kindling
pip install .
```
The `fhir kindling` command should now be available in your shell (with the venv enabled) test it with
`fhir_kindling --help`


## Usage
With the virtual environment activated you can use the cli directly from the command line directly

## Uploading a bundle to a server
```shell
fhir_kindling <path-to-bundle.json> --url <base-url-fhir-api> -u <username> -p <password> --token <token>
```

## Credits
All the FHIR resource validation is done via the [fhir.resources](https://github.com/nazrulworld/fhir.resources) package.
The CLI was built using [click](https://click.palletsprojects.com/en/8.0.x/).
This package was created with Cookiecutter and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter) project template.
