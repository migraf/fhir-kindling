from typing import List
from functools import cache

from requests import Response
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle
from fhir.resources.reference import Reference


class CreateResponse:
    @staticmethod
    def _process_location_header(server_create_response: dict):
        # todo check for different fhir server types
        location_header: str = server_create_response.get("Location", server_create_response.get("location"))
        if not location_header:
            raise ValueError("Location field not found.")
        split_location = location_header.split("/")
        location = "/".join(split_location[:-2])
        version = int(split_location[-1])
        resource_id = split_location[-3]
        return resource_id, location, version


class ResourceCreateResponse(CreateResponse):
    location: str = None
    resource: Resource = None
    version: int = None
    resource_id: str = None
    reference: Reference = None

    def __init__(self, server_response_dict: dict, resource: Resource):
        self.resource = resource
        resource_id, location, version = self._process_location_header(server_response_dict)
        self.location = location
        self.resource_id = resource_id
        self.resource.id = resource_id
        self.reference = Reference(**{
            "reference": self.resource.get_resource_type() + "/" + resource_id
        })


class BundleCreateResponse:
    create_responses: List[ResourceCreateResponse] = None

    def __init__(self, server_response: Response, bundle: Bundle):
        self.create_responses = []
        for i, entry in enumerate(server_response.json()["entry"]):
            resource = bundle.entry[i].resource
            create_response = ResourceCreateResponse(entry["response"], resource)
            self.create_responses.append(create_response)

    @property
    @cache
    def resources(self):
        return [r.resource for r in self.create_responses]

    @property
    @cache
    def references(self):
        return [r.reference for r in self.create_responses]


class UpdateResponse:
    def __init__(self, server_response: Response):
        pass


class SearchResponse:
    pass
