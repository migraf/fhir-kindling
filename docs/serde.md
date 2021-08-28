This library as well as the CLI provides some functionality to serialize, deserialize FHIR resources and bundles

## Deserialization

Loading previously created bundles can be achieved with the load bundle method. It also provides the option to validate
the entries in the bundle and display potential errors in the bundle that can then be fixed.

::: fhir_kindling.serde.bundle.load_bundle
    rendering:
      heading_level: 3
      show_root_heading: True
      show_root_full_path: False


## Serialization

Parsing fhir bundles and resources into a tabular format can be achieved by the flattening the resources in the bundle.
Since a bundle can contain multiple different resources, the parse currently creates columns for the field of each
resource if they do not yet exist. If a column already exists then it can be used otherwise it will be created.

::: fhir_kindling.serde.flatten_bundle
    rendering:
      heading_level: 3
      show_root_heading: True
      show_root_full_path: False

