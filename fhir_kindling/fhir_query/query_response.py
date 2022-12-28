import pathlib
from typing import Union, List, Dict, Optional
from enum import Enum

import orjson
from fhir.resources.bundle import Bundle
from fhir.resources import FHIRAbstractModel
from pydantic import BaseModel
import httpx


from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters


class OutputFormats(Enum):
    """
    Enum for the output formats.
    """

    JSON = "json"
    XML = "xml"


class DataframeFormat(Enum):
    LIST = "list"
    SINGLE = "single"


class IncludedResources(BaseModel):
    """
    Container for resources included in the query via the _include/_revinclude parameters.
    """

    resource_type: str
    resources: Optional[List[FHIRAbstractModel]] = None


class ResponseStatusCodes(str, Enum):
    OK = 200
    CREATED = 201
    NOT_FOUND = 404
    BAD_REQUEST = 400
    INTERNAL_SERVER_ERROR = 500


class QueryResponse:
    """
    Response object for the results of a FHIR query executed against a FHIR server.
    """

    def __init__(
        self,
        response: Union[httpx.Response, str, dict],
        query_params: FHIRQueryParameters,
        output_format: OutputFormats = OutputFormats.JSON,
        limit: int = None,
        count: int = None,
    ):

        self.format = output_format
        self._limit = limit
        self.query_params = query_params
        self.resource = query_params.resource
        self._resources = None
        self._included_resources = {}
        self._bundle = None
        self.status_code: ResponseStatusCodes = None
        self.count = count

        # parse the response after the rest of the setup is complete
        self.response: Union[str, dict] = self._process_server_response(response)

    @property
    def resources(self) -> List[FHIRAbstractModel]:
        """
        List of primary resources returned by the server.

        Returns:
            List of FHIRResourceModel objects returned by the server.

        """
        if self.format == OutputFormats.XML:
            raise NotImplementedError("Resource parsing not supported for xml format")
        else:
            # return empty list if no resource matched the query
            if not self.response.get("entry"):
                return []
            if self._resources is None:
                self._extract_resources()
            return self._resources

    @property
    def included_resources(self) -> List[IncludedResources]:
        """
        Returns the list of resources included in the search.
        Returns:
            List of IncludeResources objects containing the resource type and the list of resources of this type
            included in the search

        """
        if self.format == OutputFormats.XML:
            raise NotImplementedError("Resource parsing not supported for xml format")
        else:
            # return empty list if no resource matched the query
            if not self.response.get("entry"):
                return []
            if not self.query_params.include_parameters:
                return []
            # parse the included resources if they don't exist
            if not self._included_resources:
                self._extract_resources()

            included = []
            for resource_type, resources in self._included_resources.items():
                included.append(
                    IncludedResources(resource_type=resource_type, resources=resources)
                )
            return included

    def save(self, file_path: Union[str, pathlib.Path], output_format: str = "json"):
        """
        Save the response to a file.
        Args:
            file_path: path to the file to save the response to.
            output_format: output format one of xml|json

        Returns:
            None
        """

        if isinstance(file_path, str):
            file_path = pathlib.Path(file_path)

        output_format = OutputFormats(output_format)
        # check that only xml queries can be saved as xml
        if self.format == OutputFormats.XML:
            if not output_format == OutputFormats.XML:
                raise NotImplementedError("XML query results can only be saved as XML")

        self.format = output_format
        if self.format == OutputFormats.XML:
            with open(file_path, "w") as f:
                f.write(self.response)

        elif self.format == OutputFormats.JSON:
            with open(file_path, "wb") as f:
                # dump the response as json using orjson and indent 2
                f.write(orjson.dumps(self.response, option=orjson.OPT_INDENT_2))

    def _extract_resources(self):
        """
        Parse the resources from the server response bundle. Split into included resources and resources that match the
        query exactly.
        Returns:

        """
        if not self._resources:
            self._resources = []
        for entry in Bundle(**self.response).entry:

            # add the directly queried resource to the resources list
            if entry.resource.resource_type == self.resource:
                self._resources.append(entry.resource)

            # process included resources
            elif entry.search.mode == "include":
                # get list of included resources based on type, if it does not exist yet return empty list
                included_resources = self._included_resources.get(
                    entry.resource.resource_type, []
                )
                # update the list with the entry and update the included resources dict
                included_resources.append(entry.resource)
                self._included_resources[
                    entry.resource.resource_type
                ] = included_resources

    def _process_server_response(
        self, response: Union[httpx.Response, str]
    ) -> Union[Dict, Bundle, str]:
        """
        Handle the initial response from the server and resolve pagination if necessary.
        Args:
            response: the initial server response

        Returns:
            the server response, with pagination resolved if necessary

        """

        # if the format is xml resolve pagination and return xml string response
        if self.format == OutputFormats.XML:
            if isinstance(response, httpx.Response):
                response = response.content
            return response
        # otherwise, resolve json pagination and process further according to selected outcome
        else:
            if isinstance(response, httpx.Response):
                response = response.json()
            elif isinstance(response, dict):
                response = response
            else:
                response = Bundle.parse_raw(response).dict()
            return response

    def __repr__(self):
        if self.format == OutputFormats.XML:
            return f"<QueryResponse(resource={self.resource}, format=xml)>"
        if self._included_resources:
            resources = list(self._included_resources.keys())
            return (
                f"<QueryResponse(resource={self.resource}, format=json, "
                f"included_resources={resources})>"
            )
        return f"<QueryResponse(resource={self.resource}, n={len(self.resources)})>"
