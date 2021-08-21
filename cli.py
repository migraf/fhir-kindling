"""Console script for fhir_kindling."""
import sys
import click
import yaml
from fhir_kindling.patient import PatientGenerator


@click.group()
def cli():
    """Command line interface for generating FHIR resources"""
    pass


@cli.command()
@click.option("-f", "--file", default=None, help="Path to a .yml file defining the generation specs.")
@click.option("-n", "--n-patients", default=None, help="How many patients to generate", type=int)
@click.option("-a", "--age-range", default=None, help="Space separated min/max age of patients.",
              type=click.Tuple([int, int]))
@click.option("-o", "--output", default=None, help="Path where the generated resource bundle should be stored.")
def generate(file, n_patients, age_range, output):
    """Generate FHIR resource bundles"""
    if file:
        click.echo(f"Generating FHIR resources defined in:\n{file}")
        with open(file, "r") as f:
            resource_specs = yaml.safe_load(f)
            click.echo(resource_specs)
    else:
        if not n_patients:
            n_patients = click.prompt("Enter the number of patients you want to create", default=100)
        if not age_range:
            min_age = click.prompt("Enter the min age patients", default=18, type=int)
            max_age = click.prompt("Enter the max age patients", default=101, type=int)
            click.echo(f"Min: {min_age}, max: {max_age}")

            age_range = (min_age, max_age)
        patients = PatientGenerator(n_patients, age_range=age_range).generate()

        if click.confirm("Generate additional resources for patients?"):
            patient_resource = click.prompt("Select resource:", type=click.Choice(["Observation", "Condition"]))
        else:
            pass

    if not output:
        if click.confirm("No storage location given. Exit without saving generated resources?"):
            return 0
        else:
            output = click.prompt("Enter the path or filename under which the bundle should be stored")

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
