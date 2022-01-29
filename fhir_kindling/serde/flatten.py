from typing import Union, List
from collections import MutableMapping

import pandas as pd
from fhir.resources import FHIRAbstractModel
from fhir.resources.fhirresourcemodel import FHIRResourceModel


def flatten_resources(resources: Union[List[FHIRResourceModel], List[FHIRAbstractModel]]) -> pd.DataFrame:
    """
    Flatten a list of resources of a single resource type into a dataframe.
    Args:
        resources: list of resources

    Returns: pandas dataframe with columns corresponding to the flatten ed resource keys

    """

    flat_resources = []
    for resource in resources:
        flat_resources.append(flatten_resource(resource))
    return pd.DataFrame.from_records(flat_resources)


def flatten_resource(resource: Union[FHIRResourceModel, FHIRAbstractModel]) -> dict:
    """
    Flatten a resource into a single level dictionary.
    Args:
        resource: Fhir resource to convert to single level dict

    Returns: dictionary with only single level keys containing the fields of the resource

    """
    resource_dict = resource.dict(exclude_none=True)
    flat_dict = flatten_dict(resource_dict)
    return flat_dict


def flatten_dict(d, parent_key='', sep='_') -> dict:
    """
    Flatten a nested dictionary into a single level dictionary.

    Extension of https://stackoverflow.com/a/6027615/3838313 capable of handling lists
    Args:
        d: dictionary to flatten
        parent_key: parent key user for recursion
        sep: separator for the nested keys

    Returns:

    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, MutableMapping):
                    items.extend(flatten_dict(item, f"{new_key}_{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}_{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)
