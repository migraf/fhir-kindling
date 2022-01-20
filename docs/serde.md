## Serialization

Parsing fhir bundles and resources into a tabular format can be achieved by the flattening the resources in the bundle.
Since a bundle can contain multiple different resources, the parse currently creates columns for the field of each
resource if they do not yet exist. If a column already exists then it can be used otherwise it will be created.

::: fhir_kindling.serde.flatten_bundle
    rendering:
      heading_level: 3
      show_root_heading: True
      show_root_full_path: False

