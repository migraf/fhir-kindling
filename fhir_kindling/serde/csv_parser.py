import pandas as pd
from typing import Union
from pathlib import Path
import json


def flatten_bundle(bundle_json: Union[dict, str, Path]) -> pd.DataFrame:
    if not isinstance(bundle_json, dict):
        with open(bundle_json, "r") as bundle_file:
            bundle_json = json.load(bundle_file)

    total_column_names = set()
    resource_column_values = []

    for entry in bundle_json["entry"]:
        entry_resource = entry["resource"]
        parse_result = {
            "keys": [],
            "column_vals": {}
        }
        _parse_resource(parse_result, entry_resource)

        total_column_names.update(set(parse_result["keys"]))
        resource_column_values.append(parse_result["column_vals"])

    df_dict_list = []
    for value_dict in resource_column_values:
        all_keys_dict = dict()
        for column_name in total_column_names:
            all_keys_dict[column_name] = value_dict.get(column_name, None)

        df_dict_list.append(all_keys_dict)

    df = pd.DataFrame(df_dict_list)

    return df


def _parse_resource(result, resource: dict):
    # todo cleanup recursion to directly return results
    # todo check third level of recursion and if keys need to be passed along
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

            elif isinstance(item[0], dict):
                for sub_item in item:
                    _parse_resource(result, sub_item)

        elif isinstance(item, dict):
            for sub_key, sub_item in item.items():
                if isinstance(sub_item, dict):
                    _parse_resource(result, item)
                elif isinstance(sub_item, list):
                    pass
                else:
                    composite_key = key + "." + sub_key
                    result["keys"].append(composite_key)
                    result["column_vals"][composite_key] = sub_item
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
