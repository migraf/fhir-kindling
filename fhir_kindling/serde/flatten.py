from typing import Union, List
from collections.abc import MutableMapping

import pandas as pd
from fhir.resources import FHIRAbstractModel
from fhir.resources.fhirresourcemodel import FHIRResourceModel

from fhir_kindling.fhir_query.query_response import QueryResponse


def flatten(
    resources: Union[List[FHIRResourceModel], List[FHIRAbstractModel]] = None,
    response: QueryResponse = None,
    save: bool = False,
    path: str = None,
    display_progress: bool = False,
) -> Union[pd.DataFrame, List[pd.DataFrame], None]:
    """
    Flatten a list of resources or a query response into a dataframe/multiple dataframes.
    Args:
        resources: list of resources
        response: fhir kindling query response possibly containing multiple resources
        save: save the output to one or multiple csv files
        path: path to save the csv files
        display_progress: display a progress bar

    Returns: pandas dataframe with columns corresponding to the flattened resource keys

    """
    if resources and response:
        raise ValueError("Only one of resources or response can be provided")
    if resources:
        return flatten_resources(resources)
    elif response:
        return flatten_response(response)
    else:
        raise ValueError("Either resources or response must be provided")


def flatten_response(
    response: QueryResponse,
) -> Union[pd.DataFrame, List[pd.DataFrame]]:
    """
    Flatten a query response into a dataframe/multiple dataframes.
    Args:
        response: fhir kindling query response possibly containing multiple resources

    Returns: pandas dataframe with columns corresponding to the flattened resource keys

    """
    included_resources = response.included_resources
    # Flatten the included resources into a list of dataframes
    if included_resources:
        dfs = []
        for resource in included_resources:
            dfs.append(flatten_resources(resource.resources))

        dfs.insert(0, flatten_resources(response.resources))
        return dfs
    else:
        return flatten_resources(response.resources)


def flatten_resources(
    resources: Union[List[FHIRResourceModel], List[FHIRAbstractModel]]
) -> pd.DataFrame:
    """
    Flatten a list of resources of a single resource type into a dataframe.
    Args:
        resources: list of resources
    Returns: pandas dataframe with columns corresponding to the flattened resource keys

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


def flatten_dict(
    d, parent_key: str = "", sep: str = "_", keys: List[str] = None
) -> dict:
    """
    Flatten a nested dictionary into a single level dictionary.

    Extension of https://stackoverflow.com/a/6027615/3838313 capable of handling lists
    Args:
        d: dictionary to flatten
        parent_key: parent key user for recursion
        sep: separator for the nested keys
        keys: list of keys to keep, all other keys will be skipped

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
