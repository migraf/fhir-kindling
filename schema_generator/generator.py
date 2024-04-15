import json
import pathlib
import subprocess
from typing import Literal

from generate_r4b import generate_r4b


class FhirSchemaGenerator:
    def __init__(
        self, schema_path: pathlib.Path | str, version: Literal["r4b", "r5"] = "r4b"
    ):
        if isinstance(schema_path, str):
            schema_path = pathlib.Path(schema_path)
        self.schema_path = schema_path
        self.version = version

    def _load_schema(self):
        with open(self.schema_path) as f:
            schema = json.load(f)

        return schema

    def generate(self):
        schema = self._load_schema()
        # gen_ouput = self.run_codegen()

        if self.version == "r4b":
            # TODO use gen output
            generate_r4b(schema, "")

    def run_codegen(self):
        """Run datamodel-codegen"""
        print("Running codegen wi")

        command = [
            "datamodel-codegen",
            "--input",
            str(self.schema_path.absolute()),
            "--input-file-type",
            "jsonschema",
            "--output",
            f"{self.version}.py",
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--keep-model-order",
            "--reuse-model",
            "--use-field-description",
        ]

        result = subprocess.run(command, capture_output=True, text=True).stdout
        return result


if __name__ == "__main__":
    parent_dir = pathlib.Path(__file__).parent
    definitions_file_v4b = parent_dir / "definitions" / "schema_v4b.json"
    definitions_file_v5 = parent_dir / "definitions" / "schema_v5.json"

    generator = FhirSchemaGenerator(definitions_file_v4b, "r4b")
    generator.generate()

    # generator = FhirSchemaGenerator(definitions_file_v5, "r5")
    # generator.run_codegen()
