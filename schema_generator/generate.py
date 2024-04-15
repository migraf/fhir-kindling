import pathlib
import subprocess


def generate_schemas():
    """Generate FHIR schema using datamodel-codegen"""
    print("running generate_schema")

    # path to current dir
    parent_dir = pathlib.Path(__file__).parent
    # defintiions file
    definitions_file_v4b = parent_dir / "definitions" / "schema_v4b.json"
    definitions_file_v5 = parent_dir / "definitions" / "schema_v5.json"

    print("generating schema for v4b...", end=" ")
    # TODO Fix errors automatically
    # TODO Move Base Class to the end and remove model rebuilds
    output_dir = parent_dir
    # output_dir  = parent_dir.parent / "fhir_kindling" / "resources"
    v4_outputfile = output_dir / "v4b.py"
    run_codegen(
        str(definitions_file_v4b.absolute()),
        str(v4_outputfile.absolute()),
        "V4BResource",
    )
    # _fix_fhir_errors(v4_outputfile, "v4b")
    print("done")

    print("generating schema for v5...", end=" ")
    v5_outputfile = output_dir / "v5.py"
    run_codegen(
        str(definitions_file_v5.absolute()), str(v5_outputfile.absolute()), "V5Resource"
    )
    print("done")


def run_codegen(input_file: str, output_file: str, class_name: str | None = None):
    """Run datamodel-codegen"""

    command = [
        "datamodel-codegen",
        "--input",
        input_file,
        "--input-file-type",
        "jsonschema",
        # "--output",
        # output_file,
        "--output-model-type",
        "pydantic_v2.BaseModel",
        # "--use-annotated",
        "--collapse-root-models",
        "--keep-model-order",
        "--reuse-model",
        "--use-field-description",
    ]

    if class_name:
        command.extend(["--class-name", class_name])
    result = subprocess.run(command)
    print(result)


def _fix_fhir_errors(path, version="v4b"):
    """Fix errors in generated schema"""
    if version == "v4b":
        path = path / "v4b.py"
        with open(path, "r") as file:
            lines = file.readlines()

        # Quote the Class defintions for the resource list etc.
        to_fix_lines = (392, 532)
        for line in to_fix_lines:
            lines[line] = " " * 12 + f'"{lines[line].strip()[:-1]}",\n'

        to_fix_lines = (691, 831)
        for line in to_fix_lines:
            lines[line] = " " * 12 + f'"{lines[line].strip()[:-1]}",\n'

        output_path = path.parent / "v4b_fixed.py"
        with open(output_path, "w") as file:
            file.writelines(lines)


if __name__ == "__main__":
    path = pathlib.Path(__file__).parent
    # _fix_fhir_errors(path, "v4b")
    generate_schemas()
