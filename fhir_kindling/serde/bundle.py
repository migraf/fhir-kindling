import json
from typing import Union, List

import click
from fhir.resources.bundle import BundleEntry, Bundle
from pydantic.error_wrappers import ValidationError
from pathlib import Path


def load_bundle(bundle_path: Union[Path, str], validate: bool = True) -> Union[Bundle, dict]:
    """Loads a FHIR bundle stored as a json file from file and returns a bundle object. When validate is selected
    all resource entries in the bundle are individually validated. The full bundle is validated by default.

    Args:
      bundle_path: path to the bundle file
      validate: boolean on whether to validate individual resources

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
            raise ValueError("Invalid bundle format")
        return bundle
    return bundle_json


def validate_bundle(bundle_json: dict,
                    show_invalid_entries: bool = True,
                    drop_invalid_entries: bool = False) -> Union[None, Bundle, List[int]]:
    """Validate the all the resources in the bundle and display validation errors.
    If drop

    Args:
      drop_invalid_entries: if True drops all entries in the bundle detected as invalid from the bundle entries
        and attempts tp make a new bundle with only valid entries
      bundle_json: dictionary based on a loaded json bundle
      show_invalid_entries: if True show the entries detected as invalid and the validation errors

    Returns:
        either a Bundle object if the validation succeeded or None if it failed.
    """
    if drop_invalid_entries:
        valid_entries = _validate_bundle_entries(
            bundle_json["entry"],
            show_invalid_entries=show_invalid_entries,
            drop_invalid_entries=drop_invalid_entries)
        bundle_json["entry"] = valid_entries
        try:
            bundle = Bundle(**bundle_json)
            return bundle

        except ValidationError as e:
            click.echo("Bundle could not be validated", err=True)
            if show_invalid_entries:
                click.echo(e, err=True)
            return None

    else:
        errors, error_indices = _validate_bundle_entries(
            bundle_json["entry"],
            show_invalid_entries=show_invalid_entries,
            drop_invalid_entries=drop_invalid_entries
        )

        if errors == 0:
            # Try to validate the full bundle
            try:
                bundle = Bundle(**bundle_json)
                return bundle

            except ValidationError as e:
                click.echo("Bundle could not be validated", err=True)
                if show_invalid_entries:
                    click.echo(e, err=True)
                return None
        else:
            return error_indices


def _validate_bundle_entries(entries: List[dict],
                             show_invalid_entries: bool = True,
                             drop_invalid_entries: bool = False):
    errors = 0
    error_indices = []

    valid_bundle_entries = []

    for index, entry in enumerate(entries):
        try:
            bundle_entry = BundleEntry(**entry)
            valid_bundle_entries.append(bundle_entry)
        # Catch and display validation errors and display them with their index
        except ValidationError as e:
            if show_invalid_entries:
                click.echo(f"Bundle entry with index {index} could not be validated", err=True)
                click.echo(f"\n {e} \n", err=True)
                click.echo(json.dumps(entry, indent=2), err=True)
            errors += 1
            error_indices.append(index)

    # drop invalid is set return only the validated entries
    if drop_invalid_entries:
        return valid_bundle_entries

    return errors, error_indices
