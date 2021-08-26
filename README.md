[![PyPI version shields.io](https://img.shields.io/pypi/v/ansicolortags.svg)](https://pypi.python.org/pypi/fhir_kindling)
[![Travis status](https://img.shields.io/travis/migraf/fhir_kindling.svg)](https://travis-ci.com/migraf/fhir_kindling)
[![Documentation Status](https://readthedocs.org/projects/ansicolortags/badge/?version=latest)](https://fhir-kindling.readthedocs.io/en/latest/?version=latest)



# FHIR Kindling
FHIR resource generator and synthetic data set creation and management tool.

## Features
- CLI for step by step data set/ FHIR resource creation
- Storing and loading configurations as `.yml` files
- Bundle creation and data set management on a FHIR server via the REST API


## Installation
In a virtual environment clone the project and install it using pip:
```shell
cd fhir_kindling
pip install .
```
The `fhir kindling` command should now be available in your shell test it with `fhir_kindling --help`


## Usage
With the virtual environment activated you can use the cli directly from the command line directly

## Uploading a bundle to a server
```shell
fhir_kindling <path-to-bundle.json> --url <base-url-fhir-api> -u <username> -p <password> --token <token>
```


## Credits
This package was created with Cookiecutter and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter) project template.





