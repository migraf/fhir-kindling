import json
from typing import Union

import click
from fhir.resources.bundle import BundleEntry, Bundle
from pydantic.error_wrappers import ValidationError
from pathlib import Path


def load_bundle(bundle_path: Union[Path, str], validate: bool = True) -> Bundle:
    """Loads a FHIR bundle stored as a json file from file and returns a bundle object. When validate is selected
    all resource entries in the bundle are individually validated. The full bundle is validated by default.

    Args:
      bundle_path: path to the bundle file
      validate: boolean on whether to validate individual resources
      bundle_path: Union[Path, str]:
      validate: bool:  (Default value = True)

    Returns:
      a bundle object based on the given file

    Raises:
      ValidationError: when FHIR constraints on the bundle are not met

    """
    with open(bundle_path, "r") as f:
        bundle_json = json.load(f)
    if validate:
        bundle = validate_bundle(bundle_json)
        if not bundle:
            raise ValidationError()
    else:
        bundle = Bundle(**bundle_json)
    return bundle


def validate_bundle(bundle_json: dict, show_invalid_resources: bool = True) -> Union[None, Bundle]:
    """Validate the all the resources in the bundle and display validation errors.

    Args:
      bundle_json: dictionary based on a loaded json bundle
      show_invalid_resources: bool:  (Default value = True)

    Returns:

    """

    # validate entries
    errors = 0
    for index, entry in enumerate(bundle_json["entry"]):
        try:
            bundle_entry = BundleEntry(**entry)
        except ValidationError as e:
            click.echo(f"Bundle entry with index {index} could not be validated", err=True)
            click.echo(f"\n {e} \n", err=True)
            if show_invalid_resources:
                click.echo(json.dumps(entry, indent=2), err=True)
            errors += 1
    if errors == 0:
        try:
            bundle = Bundle(**bundle_json)
            return bundle

        except ValidationError as e:
            click.echo("Bundle could not be validated", err=True)
            click.echo(e, err=True)
            return None


def _cleanup_references(bundle):
    pass
