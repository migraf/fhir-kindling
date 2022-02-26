from typing import Union, List, Tuple

from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.resource import Resource
from fhir.resources.fhirtypes import ReferenceType
from fhir.resources import FHIRAbstractModel

from fhir_kindling.fhir_query.query_response import QueryResponse
from fhir_kindling.util.resources import get_resource_fields


def extract_references(resource: Union[Resource, FHIRAbstractModel]) -> List[Tuple[str, str]]:
    """
    Extracts the references from a resource and returns them as a list of dicts.
    Args:
        resource: fhir resource object to extract references from.

    Returns: list of dicts containing the reference information.

    """
    fields = get_resource_fields(resource)

    references = []
    for field in fields:
        if field.type_ == ReferenceType:
            field_value = getattr(resource, field.name)
            if field_value:
                references.append(tuple(field_value.dict(exclude_none=True)["reference"].split("/")))
    return references


def validate_references(response: QueryResponse = None) -> List[str]:
    """
    Checks the references in a query response to ensure that the referenced resources exist in the
    response.

    :param response: The query response from which to extract references.
    :return: A list with all missing references
    """
    resources = _resource_ids_from_query_response(response)
    referenced_resources = _references_from_query_response(response)

    missing_references = []
    for ref_resource, ref_ids in referenced_resources.items():

        for ref_id in ref_ids:
            if resources.get(ref_resource):
                if ref_id not in resources[ref_resource]:
                    missing_references.append(f"{ref_resource}/{ref_id}")
            else:
                missing_references.append(f"{ref_resource}/{ref_id}")
    return missing_references


def _references_from_query_response(response: QueryResponse) -> dict:
    references = {}
    for resource in response.resources:
        _update_reference_set(references, resource)
    for included_resource in response.included_resources:
        for resource in included_resource.resources:
            _update_reference_set(references, resource)

    return references


def _update_reference_set(references: dict, resource: Union[Resource, FHIRAbstractModel]):
    resource_references = extract_references(resource)
    for reference in resource_references:
        reference_set = references.get(reference[0])
        if reference_set is None:
            reference_set = set()
        reference_set.add(reference[1])
        references[reference[0]] = reference_set


def _resource_ids_from_query_response(response: QueryResponse) -> dict:
    contained_resources = {}
    for resource in response.resources:
        resource_id_set = contained_resources.get(resource.resource_type)
        if resource_id_set is None:
            resource_id_set = {resource.id}
        else:
            resource_id_set.add(resource.id)
        contained_resources[resource.resource_type] = resource_id_set

    for included_resource in response.included_resources:
        resource_id_set = contained_resources.get(included_resource.resource_type)
        if resource_id_set is None:
            resource_id_set = set()
        for resource in included_resource.resources:
            resource_id_set.add(resource.id)
        contained_resources[included_resource.resource_type] = resource_id_set

    return contained_resources
