import importlib
import inspect
import os
from pathlib import Path

# TODO re-export all fhir resources under a single module and apply some transformation on them


if __name__ == '__main__':
    resources = importlib.import_module("fhir.resources")
    print(resources.__file__)

    resource_module_path = Path(resources.__file__).parent
    for mod in list(os.listdir(resource_module_path)):
        print(mod)
        if mod.split(".")[-1] == "py":
            module = importlib.import_module(f"fhir.resources.{mod.split('.')[0]}")
            members = inspect.getmembers(module)

