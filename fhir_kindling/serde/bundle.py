import json
from typing import Union

import click
from fhir.resources.bundle import BundleEntry, Bundle
from pydantic.error_wrappers import ValidationError
from pathlib import Path


def load_bundle(bundle_path: Union[Path, str], validate: bool = True) -> Bundle:
    with open(bundle_path, "r") as f:
        bundle_json = json.load(f)
    if validate:
        bundle = validate_bundle(bundle_json)
    else:
        bundle = Bundle(**bundle_json)
    return bundle


def validate_bundle(bundle_json, show_invalid_resources: bool = False):
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
