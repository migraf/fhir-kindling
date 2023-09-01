import json
from collections import OrderedDict
from dataclasses import dataclass
from typing import List, Union

import fhir.resources
from fhir.resources.bundle import Bundle
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource
from httpx import Response


class CreateResponse:
    @staticmethod
    def _process_location_header(server_create_response: dict):
        location_header: str = server_create_response.get(
            "Location", server_create_response.get("location")
        )
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
        if isinstance(resource, OrderedDict):
            # intialize a new resource from the resource dict
            self.resource = fhir.resources.construct_fhir_element(
                resource["resourceType"], resource
            )
        else:
            self.resource = resource

        resource_id, location, version = self._process_location_header(
            server_response_dict
        )
        self.location = location
        self.resource_id = resource_id
        self.resource.id = resource_id
        self.reference = Reference(
            **{"reference": self.resource.get_resource_type() + "/" + resource_id}
        )

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(resource_id={self.resource_id}, location={self.location},"
            f" version={self.version})>"
        )


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
        return (
            f"BundleCreateResponse(create_responses={self.create_responses[0]}...{self.create_responses[-1]}, "
            f"num_resources={len(self.create_responses)})"
        )


class TransferResponse:
    origin_server: str
    destination_server: str
    create_responses: List[ResourceCreateResponse]
    linkage: dict
    n_transferred: int

    def __init__(
        self,
        origin_server: str,
        destination_server: str,
        create_responses: List[ResourceCreateResponse],
        linkage: dict = None,
    ):
        self.origin_server = origin_server
        self.destination_server = destination_server
        self.create_responses = create_responses
        self.linkage = linkage
        self.n_transferred = len(create_responses)

    def save_linkage(self, filename: str):
        with open(filename, "w") as f:
            json.dump(self.linkage, f)

    def __str__(self):
        return (
            f"TransferResponse origin({self.origin_server}) -> destination ({self.destination_server})\n"
            f"n_transferred: {self.n_transferred}, linkage: {'stored' if self.linkage else 'not stored'}"
        )

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(origin_server={self.origin_server},"
            f" destination_server={self.destination_server})"
        )


class UpdateResponse:
    # TODO: implement
    def __init__(self, server_response: Response):
        pass


@dataclass
class DeleteResponse:
    server: str
    resource_ids: List[str]

    def add_resource_ids(self, resources: List[Union[Resource, dict]]):
        resource_ids = [r["id"] if isinstance(r, dict) else r.id for r in resources]
        self.resource_ids.extend(resource_ids)
