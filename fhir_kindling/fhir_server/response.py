from typing import List

from requests import Response
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle, BundleEntry


class ServerResponse:
    def _process_location_header(self, headers: dict):
        # todo check for different fhir server types
        location_header: str = headers.get("Location")
        if not location_header:
            raise ValueError("Location field not found.")
        split_location = location_header.split("/")
        location = "/".join(split_location[:-2])
        version = int(split_location[-1])
        resource_id = split_location[-3]
        return resource_id, location, version


class ResourceCreateResponse(ServerResponse):
    location: str = None
    resource: Resource = None
    version: int = None
    resource_id: str = None

    def __init__(self, server_response_dict: dict, resource: Resource):
        self.resource = resource
        resource_id, location, version = self._process_location_header(server_response_dict)
        self.location = location
        self.resource_id = resource_id
        self.resource.id = resource_id


class BundleCreateResponse:
    create_responses: List[ResourceCreateResponse]

    def __init__(self, server_response: Response, bundle: Bundle):
        for i, entry in enumerate(server_response.json()["entry"]):
            resource = bundle.entry[i].resource
            create_response = ResourceCreateResponse(entry["response"], resource)
            self.create_responses.append(create_response)

    @property
    def resources(self):
        return [r.resource for r in self.create_responses]


class UpdateResponse:
    def __init__(self, server_response: Response):
        pass


class SearchResponse:
    pass
