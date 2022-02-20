from fhir.resources.patient import Patient

from fhir_kindling.util.resources import get_resource_fields


def test_get_resource_fields():
    fields = get_resource_fields(Patient)

    string_fields = get_resource_fields("Patient")

    assert fields == string_fields
