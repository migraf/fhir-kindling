from requests import Response
from fhir.resources.resource import Resource


class ResourceCreateResponse:
    location: str = None
    resource: Resource = None
    version: int = None
    resource_id: str = None

    def __init__(self, server_response: Response, resource: Resource):
        self.resource = resource
        self._process_location_header(server_response.headers)

    def _process_location_header(self, headers: dict):
        # todo check for different fhir server types
        location_header: str = headers.get("Location")
        if not location_header:
            raise ValueError("Location header not found.")
        split_location = location_header.split("/")
        self.location = "/".join(split_location[:-2])
        self.version = int(split_location[-1])
        self.resource_id = split_location[-3]
        self.resource.id = self.resource_id


class UpdateResponse:
    def __init__(self, server_response: Response):
        pass
