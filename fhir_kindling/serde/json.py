from typing import Union

import orjson
from fhir.resources import FHIRAbstractModel
from fhir.resources.resource import Resource


def json_dict(resource: Union[Resource, FHIRAbstractModel] = None, json_dict: dict = None) -> dict:
    if resource:
        json_dict = orjson.loads(resource.json(exclude_none=True))
        return json_dict
    elif json_dict:
        return orjson.loads(orjson.dumps(json_dict))
