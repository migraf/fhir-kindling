"""Console script for fhir_kindling."""
import sys
import click
import yaml
from fhir_kindling.generators import PatientGenerator
from .upload import upload_bundle
from .query_functions import query_server as execute_query
from fhir_kindling.fhir_server.auth import load_environment_auth_vars
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import click_spinner


@click.group()
def main():
    """Command line interface for generating synthetic FHIR resources and uploading them to a FHIR server."""
    load_dotenv(find_dotenv())


@main.command()
@click.option("-f", "--file", default=None, help="Path to a .yml file defining the generation specs.")
@click.option("-n", "--n-patients", default=None, help="How many patients to generate", type=int)
@click.option("-a", "--age-range", default=None, help="Space separated min/max age of patients.",
              type=click.Tuple([int, int]))
@click.option("-o", "--output", default=None, help="Path where the generated resource bundle should be stored.")
@click.option("--upload", is_flag=True)
@click.option("--url", default=None, help="url of the FHIR api endpoint to upload the bundle to.")
@click.option("--username", default=None, help="username for basic auth")
@click.option("--password", default=None, help="password for basic auth")
@click.option("--token", default=None, help="token for bearer token auth")
def generate(file, n_patients, age_range, output, url, upload, username, password, token):
    """Generate FHIR resource bundles and synthetic data sets"""
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
        if click.confirm("No storage location given. Exit without saving generated resources to disk?"):
            return 0
        else:
            output = click.prompt("Enter the path or filename under which the bundle should be stored",
                                  default="bundle.json")
            if Path(output).exists():
                overwrite = click.confirm(f"File already exists. Overwrite {output}?")
                if not overwrite:
                    output = click.prompt("Enter new filepath")
            with open(output, "w") as output_file:
                bundle = patient_generator.make_bundle()
                output_file.write(bundle.json(indent=2))
    click.echo(f"Storing resources in {output}")

    return 0


@main.command()
@click.argument("bundle")
@click.option("--url", help="url of the FHIR api endpoint to upload the bundle to.")
@click.option("-u", "--username", default=None, help="Password to get when authenticating against basic auth.")
@click.option("-p", "--password", default=None, help="Username to use when authenticating with basic auth.")
@click.option("-t", "--token", default=None, help="Token to use with bearer token auth.")
@click.option("-s", "--summary", is_flag=True, help="Print summary information about the upload.")
def upload(bundle, url, username, password, token, summary):
    """Upload a bundle to a fhir server"""

    # Get the url
    if not url:
        url = click.prompt("Enter the API endpoint of the fhir server you want to upload to.")

    if not username and not password and not token:
        click.echo("Attempting to load auth from environment.")
        username, password, token = load_environment_auth_vars()
    if not username and not password and not token:
        click.confirm("No auth information found. Upload without authentication?")

    if (username or password) and token:
        raise ValueError("Only one of basic or token auth can be used.")

    if username and not password:
        password = click.prompt(f"Enter your password ({username}):", hide_input=True)

    click.echo("Uploading bundle...", nl=False)
    with click_spinner.spinner():

        upload_bundle(bundle, fhir_api_url=url, username=username, password=password, token=token)
    click.echo("Resources uploaded successfully")

    return 0


@main.command()
@click.option("-q", "--query", default=None, help="FHIR API query string, appended to api url.")
@click.option("-r", "--resource", default=None, help="Identifier of the resource to query e.g. Patient")
@click.option("--url", help="url of the FHIR api endpoint to query against.")
@click.option("-f", "--file", default=None, help="File in which to save the query results")
@click.option("-o", "--output_format", default="json", help="Format in which to store the results.")
@click.option("-u", "--username", default=None, help="Username to get when authenticating with basic auth.")
@click.option("-p", "--password", default=None, help="Password to use when authenticating with basic auth.")
@click.option("--token", default=None, help="Token to use with bearer token auth.")
def query(query, resource, url, file, output_format, username, password, token):
    """Query resources from a fhir server"""

    if not (username and password) or token:
        click.echo("Attempting to find authentication in environment variables...", err=True, nl=False)
        username, password, token = load_environment_auth_vars()

        if (username and password) or token:
            click.echo("Success")
        else:
            click.echo()
            click.confirm("Continue without authentication?")

    click.echo("Executing query...", nl=False)
    with click_spinner.spinner():
        if query:
            # todo fix fhir server type and solve this in a nicer a way
            response = execute_query(query_string=query, out_path=file, out_format=output_format,
                                     fhir_server_type="hapi",
                                     username=username, password=password, fhir_server_url=url, token=token)
        if resource:
            response = execute_query(resource=resource, out_path=file, out_format=output_format,
                                     fhir_server_type="hapi",
                                     username=username, password=password, fhir_server_url=url, token=token)
    if not file:
        click.echo()
        click.echo_via_pager(response)
    else:
        click.echo()
        click.echo(f"Stored results at {file}")

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
