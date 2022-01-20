import collections
import json
import pathlib
from typing import Union, List, Dict, Optional
from enum import Enum

from fhir.resources.bundle import Bundle
from fhir.resources import FHIRAbstractModel
from fhir.resources.fhirresourcemodel import FHIRResourceModel
from pydantic import BaseModel
from requests import Session, Response
import xmltodict

from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters


class OutputFormats(Enum):
    JSON = "json"
    XML = "xml"
    CSV = "csv"


class IncludedResources(BaseModel):
    resource_type: str
    resources: Optional[List[FHIRAbstractModel]] = None


class QueryResponse:

    def __init__(self,
                 session: Session,
                 response: Response,
                 query_params: FHIRQueryParameters,
                 output_format: str = "json",
                 limit: int = None):

        self.session = session
        self.format = output_format
        self._limit = limit
        self.response: Union[str, dict] = self.process_server_response(response)
        self.query_params = query_params
        self.resource = query_params.resource
        self._resources = None
        self._included_resources = {}
        self._bundle = None

    def process_server_response(self, response: Response) -> Union[Dict, Bundle, str]:

        # if the format is xml resolve pagination and return xml string response
        if self.format == "xml":
            return self._resolve_xml_pagination(response)

        # otherwise, resolve json pagination and process further according to selected outcome
        else:
            json_bundle = self._resolve_json_pagination(response)
            if self.format in ["json", "dict"]:
                return json_bundle
            elif self.format == "bundle":
                return Bundle(**json_bundle)

    @property
    def resources(self) -> List[FHIRResourceModel]:
        if self.format == "xml":
            raise NotImplementedError("Resource parsing not supported for xml format")
        else:
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
        if self.format == "xml":
            raise NotImplementedError("Resource parsing not supported for xml format")
        else:
            # raise error if there aren't any included resources
            if not self.query_params.include_parameters:
                raise ValueError("No included resources defined in query.")
            # parse the included resources if they don't exist
            if not self._included_resources:
                self._extract_resources()

            included = []
            for resource_type, resources in self._included_resources.items():
                included.append(IncludedResources(resource_type=resource_type, resources=resources))
            return included

    def _extract_resources(self):
        if not self._resources:
            self._resources = []
        for entry in Bundle(**self.response).entry:

            # add the directly queried resource to the resources list
            if entry.resource.resource_type == self.resource:
                self._resources.append(entry.resource)

            # process included resources
            elif entry.search.mode == "include":
                # get list of included resources based on type, if it does not return empty list
                included_resources = self._included_resources.get(entry.resource.resource_type, [])
                # update the list with the entry and update the included resources dict
                included_resources.append(entry.resource)
                self._included_resources[entry.resource.resource_type] = included_resources

    def save(self, file_path: Union[str, pathlib.Path], format: str = "json"):

        format = OutputFormats(format)

        # check that only xml queries can be saved as xml
        if self.format == OutputFormats.XML:
            if not format == OutputFormats.XML:
                raise NotImplementedError("XML query results can only be saved as XML")

        self.format = format

        # todo improve encodings
        if self.format == OutputFormats.XML:
            with open(file_path, "w") as f:
                f.write(self.response)

        elif self.format == OutputFormats.JSON:
            with open(file_path, "w") as f:
                bundle = Bundle(**self.response)
                f.write(bundle.json(indent=2))
        elif self.format == OutputFormats.CSV:
            raise NotImplementedError("CSV format not yet supported")

    def _resolve_xml_pagination(self, server_response: Response) -> str:

        # parse the xml response and extract the initial entries
        initial_response = xmltodict.parse(server_response.text)
        entries = initial_response["Bundle"]["entry"]
        response = initial_response
        # resolve the pagination
        while True:
            next_page = False
            for link in response["Bundle"]["link"]:
                if isinstance(link, collections.OrderedDict):
                    relation_dict = dict(link["relation"])
                else:
                    break
                if relation_dict.get("@value") == "next":
                    # get url and extend with xml format
                    url = link["url"]["@value"]
                    url = url + "&_format=xml"  # todo check this
                    r = self.session.get(url)
                    r.raise_for_status()
                    response = xmltodict.parse(r.text)
                    added_entries = response["Bundle"]["entry"]
                    entries.extend(added_entries)
                    # Stop resolving the pagination when the limit is reached
                    if self._limit:
                        if len(entries) >= self._limit:
                            next_page = False
                        else:
                            next_page = True
                    else:
                        next_page = True

            if not next_page:
                print("All pages found")
                break
        # added the paginated resources to the initial response
        initial_response["Bundle"]["entry"] = entries[:self._limit] if self._limit else entries
        full_response_xml = xmltodict.unparse(initial_response, pretty=True)
        return full_response_xml

    def _resolve_json_pagination(self, server_response: Response):
        response = server_response.json()
        link = response.get("link", None)
        # If there is a link, get the next page otherwise return the response
        if not link:
            return response
        else:
            entries = []
            entries.extend(response["entry"])
            # if the limit is reached, stop resolving the pagination
            if self._limit:
                if len(entries) >= self._limit:
                    response["entry"] = response["entry"][:self._limit]
                    return response
            # query the linked page and add the entries to the response
            while response.get("link", None):
                if self._limit and len(entries) >= self._limit:
                    print("Limit reached stopping pagination resolve")
                    break

                next_page = next((link for link in response["link"] if link.get("relation", None) == "next"), None)

                if next_page:
                    response = self.session.get(next_page["url"]).json()
                    entries.extend(response["entry"])
                else:
                    break

            response["entry"] = entries[:self._limit] if self._limit else entries
            return response

    def _serialize_output(self):
        if isinstance(self.response, bytes):
            self.response = self.response.decode("utf-8")
        if isinstance(self.response, str):
            if self.format == "xml":
                return self.response
            elif self.format == "json":
                return Bundle.construct(**json.loads(self.response)).json()
            elif self.format == "dict":
                return Bundle.construct(**json.loads(self.response)).dict()
            elif self.format == "model":
                return Bundle.construct(**json.loads(self.response))

        elif isinstance(self.response, Bundle):
            if self.format == "json":
                return self.response.json(indent=2)
            elif self.format == "dict":
                return self.response.dict()
            elif self.format == "model":
                return self.response

        else:
            raise ValueError("Unable to serialize query response")
