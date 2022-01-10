import collections
import json
import pathlib
from importlib.resources import Resource
from typing import Union, List, Dict
from fhir.resources.bundle import Bundle
from requests import Session, Response
import xmltodict

from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters


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
        self.response = self.process_server_response(response)
        self.query_params = query_params
        self.resource = query_params.resource
        self._resources = None
        self._included_resources = None

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

    @property
    def resources(self) -> List[Resource]:
        if self.format == "xml":
            raise NotImplementedError("Resource parsing not supported for xml format")
        else:
            if self._resources is None:
                self._extract_resources()
            return self._resources

    @property
    def included_resources(self):
        if self.format == "xml":
            raise NotImplementedError("Resource parsing not supported for xml format")
        else:
            if not self.includes:
                raise ValueError("No included resources defined in query.")
            if self._included_resources is None:
                self._extract_resources()

            return self._included_resources

    def _extract_resources(self):
        if not self._resources:
            self._resources = []
        for entry in Bundle(**self.response).entry:

            if entry.resource.resource_type == self.resource:
                self._resources.append(entry.resource)
        # todo separate the included resources

    def to_file(self, file_path: Union[str, pathlib.Path]):

        with open(file_path, "w") as f:
            if self.format == "xml":
                f.write(self.response)

            elif self.format == "json":
                json.dump(self.response, f, indent=2)

            elif self.format in ["dict", "bundle"]:
                print("Storing as json")
                if isinstance(self.response, Bundle):
                    json.dump(self.response.dict(), f, indent=2)
                else:
                    json.dump(self.response, f)

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
