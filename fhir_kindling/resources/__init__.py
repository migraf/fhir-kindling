from inspect import isclass, getsourcefile
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
import fhir.resources

# iterate through the modules in the current package
package_dir = Path(getsourcefile(fhir.resources)).resolve().parent
for (_, module_name, _) in iter_modules([package_dir]):

    # import the module and iterate through its attributes
    module = import_module(f"{__name__}.{module_name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if isclass(attribute):
            print(attribute)
            # Add the class to this package's variables
            globals()[attribute_name] = attribute
