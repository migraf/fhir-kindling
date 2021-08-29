import pandas as pd
from typing import Union
from pathlib import Path
import json


def flatten_bundle(bundle_json: Union[dict, str, Path]) -> pd.DataFrame:
    """
    Flatten a bundle given either as a dictionary or a path into a pandas dataframe

    Args:
        bundle_json: dictionary containing the bundle or path to the json file containing the bundle

    Returns:
        pandas dataframe with the flattened representation of the json bundle
    """

    if not isinstance(bundle_json, dict):
        with open(bundle_json, "r") as bundle_file:
            bundle_json = json.load(bundle_file)

    # keep track of all unique column names in a set
    total_column_names = set()
    # store list of flat dicts containing values of flattened resources
    resource_column_values = []

    for entry in bundle_json["entry"]:
        # get resource from bundle entry and create results dict
        entry_resource = entry["resource"]
        parse_result = {
            "keys": [],
            "column_vals": {}
        }
        # recursively parse the resource dict and update the results with keys and values
        _parse_resource(parse_result, entry_resource)

        # todo needs to be improved for very large bundles
        # update the set of column names and stored values
        total_column_names.update(set(parse_result["keys"]))
        resource_column_values.append(parse_result["column_vals"])

    # Create list of dicts containing all keys present in the bundle and fill the ones they dont have with none values
    df_dict_list = []
    for value_dict in resource_column_values:
        all_keys_dict = dict()
        for column_name in total_column_names:
            all_keys_dict[column_name] = value_dict.get(column_name, None)

        df_dict_list.append(all_keys_dict)

    df = pd.DataFrame(df_dict_list)

    return df


def _parse_resource(result, resource: dict, parent_key: str = None, item_index: int = None):
    """
    Recursively parse a dictionary containing a FHIR resource and return a flattened dictionary with composed keys
    to process into a dataframe.
    Stores the found keys and the flattened object in the results dictionary passed to it

    Args:
        result: dictionary in which to store the results with result = { "keys": [], column_vals: {} }
        resource: the dictionary representation of the resource to parse.
        parent_key:
        item_index:

    Returns:

    """
    # todo cleanup recursion to directly return results
    for key, item in resource.items():
        if isinstance(item, list):
            # parse list of strings
            if isinstance(item[0], str):
                if len(item) == 1:
                    result["keys"].append(key)
                    result["column_vals"][key] = item[0]
                else:
                    for i, sub_item in enumerate(item):
                        if i > 1:
                            composite_key = f"{key}_{i}"
                        else:
                            composite_key = key
                        result["column_vals"][composite_key] = sub_item
                        result["keys"].append(composite_key)
            # if the items in the string are dictionaries recurse while passing parent information
            elif isinstance(item[0], dict):
                for i, sub_item in enumerate(item):
                    _parse_resource(result, sub_item, key, i)

        elif isinstance(item, dict):
            for sub_key, sub_item in item.items():
                composite_key = key + "." + sub_key
                if isinstance(sub_item, dict):
                    _parse_resource(result, item, composite_key)
                elif isinstance(sub_item, list):
                    pass
                # todo
                else:
                    result["keys"].append(composite_key)
                    result["column_vals"][composite_key] = sub_item
        else:
            if parent_key and item_index:
                new_key = f"{parent_key}_{item_index}.{key}"
                result["keys"].append(new_key)
                result["column_vals"][new_key] = item
            else:

                result["keys"].append(key)
                result["column_vals"][key] = item


if __name__ == '__main__':
    polar_bundle_path = "../../examples/polar/bundles/POLAR_Testdaten_UKB.json"
    gecco_bundle_path = "../../examples/gecco/bundles/GECCO_bundle_patient_2acd7a79-55d7-46ad-b3a8-5f06a063487a.json"

    flatten_bundle(polar_bundle_path)
    # result = {
    #     "keys": [],
    #     "column_vals": {}
    # }
    # parse_resource(result, single_observation)

    # print(result)
