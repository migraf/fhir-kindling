"""Console script for fhir_kindling."""
import sys
import click
import yaml
from fhir_kindling.patient import PatientGenerator
import json


@click.group()
def cli():
    """Command line interface for generating synthetic FHIR resources and uploading them to a FHIR server."""
    pass


@cli.command()
@click.option("-f", "--file", default=None, help="Path to a .yml file defining the generation specs.")
@click.option("-n", "--n-patients", default=None, help="How many patients to generate", type=int)
@click.option("-a", "--age-range", default=None, help="Space separated min/max age of patients.",
              type=click.Tuple([int, int]))
@click.option("-o", "--output", default=None, help="Path where the generated resource bundle should be stored.")
@click.option("--upload", is_flag=True)
@click.option("--url", default=None, help="url of the FHIR api endpoint to upload the bundle to.")
def generate(file, n_patients, age_range, output, url, upload):
    """Generate FHIR resource bundles"""
    if file:
        click.echo(f"Generating FHIR resources defined in:\n{file}")
        with open(file, "r") as f:
            resource_specs = yaml.safe_load(f)
            click.echo(resource_specs)
    else:
        if not n_patients:
            n_patients = click.prompt("Enter the number of patients you want to create", default=100)

        # Prompt for age range if not given
        if not age_range:
            min_age = click.prompt("Enter the min age patients", default=18, type=int)
            max_age = click.prompt("Enter the max age patients", default=101, type=int)
            age_range = (min_age, max_age)

        # Generate the patients
        patient_generator = PatientGenerator(n_patients, age_range=age_range)
        patients = patient_generator.generate()

        # TODO if FHIR server is given upload the resources to get server generated ids
        if click.confirm("Generate additional resources for patients?"):
            patient_resource = click.prompt("Select resource:", type=click.Choice(["Observation", "Condition"]))
        else:
            pass

    if upload:
        if not url:
            click.prompt("Enter your FHIR server`s API url")

    if not output:
        if click.confirm("No storage location given. Exit without saving generated resources?"):
            return 0
        else:
            output = click.prompt("Enter the path or filename under which the bundle should be stored",
                                       default="bundle.json")
            with open(output, "w") as output_file:
                bundle = patient_generator.make_bundle()
                output_file.write(bundle.json(indent=2))
    click.echo(f"Storing resources in {output}")

    return 0


@cli.command()
@click.argument("bundle")
@click.option("--url", help="url of the FHIR api endpoint to upload the bundle to.")
@click.option("-u", "--username", help="Password to get when authenticating against basic auth.")
@click.option("-p", "--password", help="Username to use when authenticating with basic auth.")
@click.option("--token", help="Token to use with bearer token auth.")
def upload(bundle, url, username, password, token):
    """Upload a bundle to a fhir server"""
    pass


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
