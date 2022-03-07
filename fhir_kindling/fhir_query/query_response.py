import collections
import pathlib
from typing import Union, List, Dict, Optional
from enum import Enum

import pandas as pd
from fhir.resources.bundle import Bundle
from fhir.resources import FHIRAbstractModel
from fhir.resources.fhirresourcemodel import FHIRResourceModel
from pydantic import BaseModel
from requests import Session, Response
import xmltodict

from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters
from fhir_kindling.serde import flatten_resources


class OutputFormats(Enum):
    """
    Enum for the output formats.
    """
    JSON = "json"
    XML = "xml"
    CSV = "csv"


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

    def __init__(self,
                 session: Session,
                 response: Response,
                 query_params: FHIRQueryParameters,
                 output_format: str = "json",
                 limit: int = None):

        self.session = session
        self.format = output_format
        self._limit = limit
        self.query_params = query_params
        self.resource = query_params.resource
        self._resources = None
        self._included_resources = {}
        self._bundle = None
        self.status_code: ResponseStatusCodes = None

        # parse the response after the rest of the setup is complete
        self.response: Union[str, dict] = self._process_server_response(response)

    @property
    def resources(self) -> List[FHIRResourceModel]:
        """
        List of primary resources returned by the server.

        Returns:
            List of FHIRResourceModel objects returned by the server.

        """
        if self.format == "xml":
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
        if self.format == "xml":
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
                included.append(IncludedResources(resource_type=resource_type, resources=resources))
            return included

    def save(self, file_path: Union[str, pathlib.Path], format: str = "json"):
        """
        Save the response to a file.
        Args:
            file_path: path to the file to save the response to.
            format: output format one of xml|json|(csv)

        Returns:
            None
        """

        if isinstance(file_path, str):
            file_path = pathlib.Path(file_path)

        format = OutputFormats(format)
        # check that only xml queries can be saved as xml
        if self.format == OutputFormats.XML:
            if not format == OutputFormats.XML:
                raise NotImplementedError("XML query results can only be saved as XML")

        self.format = format
        if self.format == OutputFormats.XML:
            with open(file_path, "w") as f:
                f.write(self.response)

        elif self.format == OutputFormats.JSON:
            with open(file_path, "w") as f:
                bundle = Bundle(**self.response)
                f.write(bundle.json(indent=2))
        elif self.format == OutputFormats.CSV:
            if self.query_params.include_parameters:
                for included_resources in self.included_resources:
                    df = flatten_resources(included_resources.resources)
                    included__resource_path = f"{file_path.parent}/{file_path.stem}_" \
                                              f"included_{included_resources.resource_type}.csv"
                    df.to_csv(included__resource_path, index=False)
            df = flatten_resources(self.resources)
            df.to_csv(file_path, index=False)

    def to_dfs(self, format: str = "list") -> Union[List[pd.DataFrame], pd.DataFrame]:
        """
        Serialize the response to a list of pandas dataframes
        Args:
            format: list of dataframe (one for each resource in the response) or single dataframe

        Returns:
            List of pandas dataframes or a single dataframe containing the resources in the query
        """

        df_format = DataframeFormat(format)

        if df_format == DataframeFormat.LIST:
            dfs = [flatten_resources(self.resources)]
            if self.query_params.include_parameters:
                for included_resources in self.included_resources:
                    dfs.append(flatten_resources(included_resources.resources))

            return dfs

        elif df_format == DataframeFormat.SINGLE:
            raise NotImplementedError("Single dataframe output format not implemented")

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
                # get list of included resources based on type, if it does not return empty list
                included_resources = self._included_resources.get(entry.resource.resource_type, [])
                # update the list with the entry and update the included resources dict
                included_resources.append(entry.resource)
                self._included_resources[entry.resource.resource_type] = included_resources

    def _process_server_response(self, response: Response) -> Union[Dict, Bundle, str]:
        """
        Handle the initial response from the server and resolve pagination if necessary.
        Args:
            response: the initial server response

        Returns:
            the server response, with pagination resolved if necessary

        """

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

    def _resolve_xml_pagination(self, server_response: Response) -> str:

        # parse the xml response and extract the initial entries
        initial_response = xmltodict.parse(server_response.text)
        entries = initial_response["Bundle"].get("entry")

        # if there are no entries, return the initial response
        if not entries:
            self.status_code = ResponseStatusCodes.NOT_FOUND
            print(f"No resources match the query - query url: {self.query_params.to_query_string()}")
            return server_response.text
        else:
            self.status_code = ResponseStatusCodes.OK
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
                        next_page = len(entries) < self._limit
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
            self.status_code = ResponseStatusCodes.OK
            return response
        else:
            entries = []
            initial_entry = response.get("entry", None)
            if not initial_entry:
                self.status_code = ResponseStatusCodes.NOT_FOUND
                print(f"No resources match the query - query url: {self.query_params.to_query_string()}")
                return response
            else:
                self.status_code = ResponseStatusCodes.OK
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
