from typing import Union, List, Tuple, Dict

from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.resource import Resource
from fhir.resources.fhirtypes import ReferenceType
from fhir.resources import FHIRAbstractModel

from fhir_kindling.fhir_query.query_response import QueryResponse
from fhir_kindling.util.resources import get_resource_fields
import networkx as nx
import matplotlib.pyplot as plt


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
                # if the field is a list of references add each of them
                if isinstance(field_value, list) or isinstance(field_value, tuple):
                    for value in field_value:
                        references.append(tuple(value.dict(exclude_none=True)["reference"].split("/")))
                # add the reference
                else:
                    references.append(tuple(field_value.dict(exclude_none=True)["reference"].split("/")))
    return references


def references_from_resource_list(resources: List[Union[Resource, FHIRAbstractModel]]) -> Dict[str, set]:
    """
    Extracts the references from a list of resources and returns them as a dict.
    Args:
        resources: list of fhir resources to extract references from.

    Returns: dict of references.

    """
    references = {}
    for resource in resources:
        _update_reference_set(references, resource)
    return references


def reference_graph(resources: List[Union[Resource, FHIRAbstractModel]], display=False) -> nx.DiGraph:
    dg = nx.DiGraph()

    for resource in resources:

        path = resource.relative_path()
        if path in dg:
            dg.nodes[path]["resource"] = resource
            print(f"adding {resource.resource_type} resource to existing path")
        else:
            print(f"adding {resource.resource_type} resource to new path")
            dg.add_node(path, resource=resource)
        for reference in extract_references(resource):

            reference_path = f"{reference[0]}/{reference[1]}"
            if reference_path not in dg:
                print(f"adding reference node {reference_path}")
                dg.add_node(reference_path, resource=None)
            dg.add_edge(reference_path, path)

    if display:
        nx.draw(dg, with_labels=True)
        plt.show()

    return dg


def check_missing_references(resources: List[Union[Resource, FHIRAbstractModel]]) -> List[str]:
    """
    Checks the references in a list of resources to ensure that the referenced resources exist in the list.
    Args:
        resources: list of fhir resources

    Returns:

    """
    references = {}
    resource_ids = {}
    for resource in resources:
        # extract references
        _update_reference_set(references, resource)
        # extract ids
        resource_id_set = resource_ids.get(resource.resource_type)
        if resource_id_set is None:
            resource_id_set = {resource.id}
        else:
            resource_id_set.add(resource.id)
        resource_ids[resource.resource_type] = resource_id_set
    missing = _get_missing_references(references, resource_ids)
    return missing


def _get_missing_references(references: dict, resource_ids: dict) -> List[str]:
    missing_references = []
    for ref_resource, reference_set in references.items():
        # get set of resource ids for this resource type
        id_set = resource_ids.get(ref_resource)
        if id_set:
            for ref_id in reference_set:
                # check if the referenced id is present in the set of ids for this resource type
                if ref_id not in id_set:
                    missing_references.append(f"{ref_resource}/{ref_id}")
        # if there are no resources of the type add all references to missing references
        else:
            missing_references.extend([f"{ref_resource}/{ref_id}" for ref_id in reference_set])
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
