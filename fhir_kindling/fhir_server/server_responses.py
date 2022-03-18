from typing import List
from requests import Response
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle
from fhir.resources.reference import Reference
from pydantic import BaseModel

from fhir_kindling.fhir_query import FHIRQueryParameters


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

    def __repr__(self):
        return f"<{self.__class__.__name__}(resource_id={self.resource_id}, location={self.location}," \
               f" version={self.version}, resource=...)>"


class BundleCreateResponse:
    create_responses: List[ResourceCreateResponse] = None

    def __init__(self, server_response: Response, bundle: Bundle):
        self.create_responses = []
        for i, entry in enumerate(server_response.json()["entry"]):
            resource = bundle.entry[i].resource
            create_response = ResourceCreateResponse(entry["response"], resource)
            self.create_responses.append(create_response)

    @property
    def resources(self):
        return [r.resource for r in self.create_responses]

    @property
    def references(self):
        return [r.reference for r in self.create_responses]

    def __repr__(self):
        return f"BundleCreateResponse(create_responses={self.create_responses[0]}...{self.create_responses[-1]}, " \
               f"num_resources={len(self.create_responses)})"


class TransferResponse:
    origin_server: str
    destination_server: str
    query_parameters: FHIRQueryParameters
    create_responses: List[ResourceCreateResponse]

    def __init__(self,
                 origin_server: str,
                 destination_server: str,
                 create_responses: List[ResourceCreateResponse],
                 query_parameters: FHIRQueryParameters):
        self.origin_server = origin_server
        self.destination_server = destination_server
        self.create_responses = create_responses
        self.query_parameters = query_parameters

    def __repr__(self):
        return f"<{self.__class__.__name__}(origin_server={self.origin_server}," \
               f" destination_server={self.destination_server}, query_parameters={self.query_parameters}," \
               f" create_responses={self.create_responses[0]}...{self.create_responses[-1]})"


class UpdateResponse:
    def __init__(self, server_response: Response):
        pass


class ResourceSummary(BaseModel):
    resource: str
    count: int


class ServerSummary(BaseModel):
    name: str
    resources: List[ResourceSummary]

    @property
    def available_resources(self) -> List[ResourceSummary]:
        return [r for r in self.resources if r.count > 0]
