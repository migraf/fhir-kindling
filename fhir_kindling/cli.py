"""Console script for fhir_kindling."""
import sys
import click
import yaml


@click.command()
@click.option("--file", default="kindling.yml", help="Path to the .yml file defining the generation specs.")
def main(file):
    """Console script for fhir_kindling."""
    click.echo("Replace this message by putting your code into "
               "fhir_kindling.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    click.echo(f"kindling file: {file}")


    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
