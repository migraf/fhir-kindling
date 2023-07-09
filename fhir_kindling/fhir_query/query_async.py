from typing import Any, Callable, List, Union

import fhir.resources
import httpx
import orjson
import xmltodict
from fhir.resources import FHIRAbstractModel
from fhir.resources.fhirresourcemodel import FHIRResourceModel

from fhir_kindling.fhir_query.base import FhirQueryBase
from fhir_kindling.fhir_query.query_parameters import (
    FhirQueryParameters,
)
from fhir_kindling.fhir_query.query_response import (
    OutputFormats,
    QueryResponse,
    ResponseStatusCodes,
)


class FhirQueryAsync(FhirQueryBase):
    def __init__(
        self,
        base_url: str,
        resource: Union[
            FHIRResourceModel, fhir.resources.FHIRAbstractModel, str
        ] = None,
        query_parameters: FhirQueryParameters = None,
        auth: httpx.Auth = None,
        headers: dict = None,
        output_format: str = "json",
        client: httpx.AsyncClient = None,
        proxies: Union[str, dict] = None,
    ):
        """Initialize an async FHIR query object.

        Args:
            base_url: Base URL of the FHIR server to query.
            resource: Base resource to build the query on. Defaults to None.
            query_parameters: Query parameters object that fully describes a FHIR query. Defaults to None.
            auth: httpx auth object to authenticate the requests. Defaults to None.
            headers: Optional additional headers to add to the request. Defaults to None.
            output_format: Response format of the query. Defaults to "json".
            client: httpx Client passed from the server. Defaults to None.
            proxies: List of proxies to use. Defaults to None.
        """
        super().__init__(
            base_url,
            resource,
            query_parameters,
            auth,
            headers,
            output_format,
        )
        self.proxies = proxies
        # set up the async client instance
        self.client = None
        if client:
            self.client = client
        else:
            self._setup_client()

    async def all(
        self,
        page_callback: Union[
            Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None
        ] = None,
        count: int = None,
    ) -> QueryResponse:
        """
        Execute the query and return all results matching the query parameters.

        Args:
            page_callback: if this argument is set the given callback function will be called for each page of results
            count: number of results in a page, default value of 50 is used when page_callback is set but no count is
        Returns:
            QueryResponse object containing all resources matching the query, as well os optional included
            resources.

        """
        self._limit = None
        self._count = count
        response = await self._execute_query(page_callback=page_callback, count=count)
        return response

    async def limit(
        self,
        n: int,
        page_callback: Union[
            Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None
        ] = None,
        count: int = None,
    ) -> QueryResponse:
        """
        Execute the query and return the first n results matching the query parameters.
        Args:
            n: number of resources to return
            page_callback: if this argument is set the given callback function will be called for each page of results
            count: number of results in a page, default value of 50 is used when page_callback is set but no count is

        Returns:
            QueryResponse object containing the first n resources matching the query, as well os optional included
            resources.

        """
        self._limit = n
        self._count = count
        response = await self._execute_query(page_callback=page_callback, count=count)
        return response

    async def first(self) -> QueryResponse:
        """
        Return the first resource matching the query parameters.
        Returns:
            QueryResponse object containing the first resource matching the query

        """
        self._limit = 1
        response = await self._execute_query(count=1)
        return response

    async def count(self) -> int:
        """
        Return the number of resources matching the query parameters.
        Returns:
            number of resources matching the query

        """

        response = await self.client.get(self.query_url + "&_summary=count")
        response.raise_for_status()
        return response.json()["total"]

    def _setup_client(self):
        headers = self.headers if self.headers else {}
        headers["Content-Type"] = "application/fhir+json"
        self.client = httpx.AsyncClient(auth=self.auth, headers=headers, timeout=None)

    async def _execute_query(
        self,
        page_callback: Union[
            Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None
        ] = None,
        count: int = None,
    ) -> QueryResponse:
        r = await self.client.get(self.query_url)
        r.raise_for_status()
        response = await self._resolve_response_pagination(r, page_callback, count)
        return response

    async def _resolve_response_pagination(
        self,
        initial_response: httpx.Response,
        page_callback: Union[
            Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None
        ] = None,
        count: int = None,
    ) -> QueryResponse:
        if self.output_format == OutputFormats.JSON:
            response = await self._resolve_json_pagination(
                initial_response, page_callback, count
            )

        else:
            response = await self._resolve_xml_pagination(initial_response)

        return QueryResponse(
            response=response,
            query_params=self.query_parameters,
            count=count,
            limit=self._limit,
            output_format=self.output_format,
        )

    async def _resolve_json_pagination(
        self,
        initial_response: httpx.Response,
        page_callback: Union[
            Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None
        ] = None,
        count: int = None,
    ) -> dict:
        response_json = orjson.loads(initial_response.content)
        link = response_json.get("link", None)
        # If there is a link, get the next page otherwise return the response
        if not link:
            self.status_code = ResponseStatusCodes.OK
            return response_json
        else:
            entries = []
            initial_entry = response_json.get("entry", None)
            if not initial_entry:
                self.status_code = ResponseStatusCodes.NOT_FOUND
                return response_json
            else:
                self.status_code = ResponseStatusCodes.OK
                response_entries = response_json["entry"]
                entries.extend(response_entries)
                self._execute_callback(response_entries, page_callback)
            # if the limit is reached, stop resolving the pagination
            if self._limit and len(entries) >= self._limit:
                response_entries = response_json["entry"][: self._limit]
                response_json["entry"] = response_entries
                self._execute_callback(response_entries, page_callback)
                return response_json
            # query the linked page and add the entries to the response
            while response_json.get("link", None):
                if self._limit and len(entries) >= self._limit:
                    break
                next_page = next(
                    (
                        link
                        for link in response_json["link"]
                        if link.get("relation", None) == "next"
                    ),
                    None,
                )
                if next_page:
                    page_response = await self.client.get(next_page["url"])
                    response_json = page_response.json()
                    response_entries = response_json["entry"]
                    entries.extend(response_entries)
                    self._execute_callback(response_entries, page_callback)
                else:
                    break

            response_json["entry"] = entries[: self._limit] if self._limit else entries
            return response_json

    async def _resolve_xml_pagination(self, server_response: httpx.Response) -> str:
        # parse the xml response and extract the initial entries
        initial_response = xmltodict.parse(server_response.text)
        entries = initial_response["Bundle"].get("entry")

        # if there are no entries, return the initial response
        if not entries:
            self.status_code = ResponseStatusCodes.NOT_FOUND
            print(
                f"No resources match the query - query url: {self.query_parameters.to_query_string()}"
            )
            return server_response.text
        else:
            self.status_code = ResponseStatusCodes.OK
        response = initial_response
        # resolve the pagination
        while True:
            next_page = False
            for link in response["Bundle"]["link"]:
                # if there is a next page, get the next page
                if not isinstance(link, dict):
                    break
                relation_dict = link.get("relation", None)
                if relation_dict.get("@value") == "next":
                    # get url and extend with xml format
                    url = link["url"]["@value"]
                    url = url + "&_format=xml"
                    r = await self.client.get(url)
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
                break
        # added the paginated resources to the initial response
        initial_response["Bundle"]["entry"] = (
            entries[: self._limit] if self._limit else entries
        )
        full_response_xml = xmltodict.unparse(initial_response, pretty=True)
        return full_response_xml
