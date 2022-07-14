from typing import Union, Callable, List, Any, TypeVar
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle
from fhir.resources.fhirresourcemodel import FHIRResourceModel
from fhir.resources import FHIRAbstractModel
import fhir.resources
from inspect import signature
import xmltodict
import collections

import httpx
from fhir_kindling.fhir_query.query_response import QueryResponse, ResponseStatusCodes
from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters, IncludeParameter, FieldParameter, \
    ReverseChainParameter, QueryOperators

T = TypeVar('T', bound='FHIRQueryBase')


class FHIRQueryBase:
    def __init__(self,
                 base_url: str,
                 resource: Union[FHIRResourceModel, fhir.resources.FHIRAbstractModel, str] = None,
                 query_parameters: FHIRQueryParameters = None,
                 auth: httpx.Auth = None,
                 headers: dict = None,
                 output_format: str = "json"):

        self.base_url = base_url

        # Set up the requests session with auth and headers
        self.auth = auth
        self.headers = headers

        # initialize the resource and query parameters
        if resource:
            if isinstance(resource, str):
                self.resource = fhir.resources.get_fhir_model_class(resource)
            elif isinstance(resource, FHIRResourceModel) or isinstance(resource, FHIRAbstractModel):
                self.resource = resource
            else:
                raise ValueError(f"resource must be a FHIRResourceModel or a string, given {type(resource)}")
            self.resource = self.resource.construct()
            self.query_parameters = FHIRQueryParameters(resource=self.resource.resource_type)

        elif query_parameters:
            self.query_parameters = query_parameters
            self.resource = fhir.resources.get_fhir_model_class(query_parameters.resource)
            self.resource = self.resource.construct()
        else:
            raise ValueError("Either resource or query_parameters must be set")

        self.output_format = output_format
        self._includes = None
        self._limit = None
        self._count = None
        self._query_response: Union[Bundle, str, None] = None

    def where(self: T,
              field: str = None,
              operator: Union[QueryOperators, str] = None,
              value: Union[int, float, bool, str, list] = None,
              field_param: FieldParameter = None,
              filter_dict: dict = None
              ) -> T:
        """
        Add search conditions regarding a specific field of the queried resource.
        Conditions can be added via FieldParameter class instance, via a dictionary or specifying condition via this
        method's parameter arguments (field, operator, value).
        Args:
            field_param: Instance of FieldParameter defining the field to filter for.
            filter_dict: dictionary containing the field to search for and the value to filter for.
            field: string specifier of the field to fileter for
            operator: comparison operator either as string or QueryOperators
            value: comparison value.

        Returns:

        """

        # evaluate arguments
        if field_param and filter_dict:
            raise ValueError("Cannot use both field_param and filter_dict")
        elif field_param and (field or operator or value):
            raise ValueError("Cannot use both field_param and kv parameters")
        elif filter_dict and (field or operator or value):
            raise ValueError("Cannot use both filter_dict and kv parameters")

        # create field parameters from the different argument options
        if isinstance(field_param, FieldParameter):
            added_query_param = field_param

        elif isinstance(filter_dict, dict):
            # todo allow for multiple filter_dicts/multiple parameters in dict
            added_query_param = FieldParameter(**filter_dict)
        elif field:
            if not (operator or operator == "") and value:
                kv_error_message = f"\n\tField: {field}\n\tOperator: {operator}\n\tValue: {value}"
                raise ValueError(f"Must provide operator and search value when using kv parameters.{kv_error_message}")
            else:

                if isinstance(operator, str):
                    operator = QueryOperators(operator)
                if isinstance(operator, QueryOperators):
                    operator = operator
                else:
                    raise ValueError(f"Operator must be a string or QueryOperators. Got {operator}")
                added_query_param = FieldParameter(field=field, operator=operator, value=value)

        else:
            raise ValueError("Must provide a valid instance of either field_param or filter_dict or the kv parameters")

        query_field_params = self.query_parameters.resource_parameters
        if isinstance(query_field_params, list) and len(query_field_params) > 0:
            query_field_params.append(added_query_param)
        else:
            query_field_params = [added_query_param]

        self.query_parameters.resource_parameters = query_field_params

        return self

    def include(self: T,
                resource: str = None,
                reference_param: str = None,
                target: str = None,
                reverse: bool = False,
                include_dict: dict = None,
                include_param: IncludeParameter = None
                ) -> T:

        """
        Specify resources related to the queried resource, which should be included in the query results.

        Args:
            resource: name of the resource from which to include related resources, has to match the main resource
                of the query
            reference_param: the reference parameter to search for
            target: further specification of the reference parameter to search for
            reverse: whether to consider reverse references
            include_dict: dictionary container the include parameters
            include_param: instance of IncludeParameter defining the include parameters

        Returns:
            Updated query instance with an added include parameter

        """

        if include_dict and include_param:
            raise ValueError("Cannot use both include_dict and include_param")
        elif include_dict and (resource or reference_param or target):
            raise ValueError("Cannot use both include_dict and kv parameters")
        elif include_param and (resource or reference_param or target):
            raise ValueError("Cannot use both include_param and kv parameters")

        if isinstance(include_dict, dict):
            added_include_param = IncludeParameter(**include_dict)
        elif isinstance(include_param, IncludeParameter):
            added_include_param = include_param
        elif resource and reference_param:
            added_include_param = IncludeParameter(resource=resource, search_param=reference_param, target=target,
                                                   reverse=reverse)
        else:
            raise ValueError(
                "Must provide a valid instance of either include_dict or include_param or the kv parameters")

        query_include_params = self.query_parameters.include_parameters
        if isinstance(query_include_params, list) and len(query_include_params) > 0:
            query_include_params.append(added_include_param)
        else:
            query_include_params = [added_include_param]

        self.query_parameters.include_parameters = query_include_params

        return self

    def has(self: T,
            resource: str = None,
            reference_param: str = None,
            search_param: str = None,
            operator: QueryOperators = None,
            value: Union[int, float, bool, str, list] = None,
            has_param_dict: dict = None,
            has_param: ReverseChainParameter = None
            ) -> T:
        """
        Specify query parameters for other resources that are referenced by the queried, only the resources whose
        referenced resources match the specified search criteria are included in the results.

        Args:
            resource: type of resource that references the selected resource
            reference_param: name of the field of the related resource that defines the relation
            search_param: field of the resource to compare with the given value using the given query operator
            operator: comparison operator, one of QueryOperators
            value: the value to compare the field to
            has_param_dict: dictionary containing the required reverse chain parameters as keys
            has_param: instance of ReverseChainParameter object

        Returns:
            Updated query object with an added ReverseChainParameter

        """

        # validate method input
        if has_param_dict and has_param:
            raise ValueError("Cannot use both has_param_dict and has_param")
        elif has_param_dict and (resource or reference_param or search_param or operator or value):
            raise ValueError("Cannot use both has_param_dict and kv parameters")
        elif has_param and (resource or reference_param or search_param or operator or value):
            raise ValueError("Cannot use both has_param and kv parameters")

        # parse ReverseChainParameter from method input
        if isinstance(has_param_dict, dict):
            added_has_param = ReverseChainParameter(**has_param_dict)
        elif isinstance(has_param, ReverseChainParameter):
            added_has_param = has_param
        elif resource and reference_param and search_param and operator and value:
            added_has_param = ReverseChainParameter(resource=resource, reference_param=reference_param,
                                                    search_param=search_param, operator=operator, value=value)
        else:
            raise ValueError(
                "Either has_param_dict, a parameter instance or a valid set of kv parameters must be provided")

        query_has_params = self.query_parameters.has_parameters
        if isinstance(query_has_params, list) and len(query_has_params) > 0:
            query_has_params.append(added_has_param)
        else:
            query_has_params = [added_has_param]
        self.query_parameters.has_parameters = query_has_params

        return self

    def _make_query_string(self) -> str:
        query_string = self.base_url + self.query_parameters.to_query_string()

        if not self._count:
            self._count = 5000

        if self._limit and self._limit < self._count:
            query_string += f"&_count={self._limit}"
        else:
            query_string += f"&_count={self._count}"
        query_string += f"&_format={self.output_format}"

        return query_string

    def set_query_string(self, raw_query_string: str):
        """
        Use a raw query string to set the query parameters.
        e.g. /Patient?_id=123&_lastUpdated=gt2019-01-01

        Args:
            raw_query_string: Query string to set the query parameters

        Returns:
            Query object with the query parameters set based on the raw query string

        """
        query_parameters = FHIRQueryParameters.from_query_string(raw_query_string)
        self.query_parameters = query_parameters
        return self

    @property
    def query_url(self) -> str:
        """
        Display the query URL that will be used to execute the query.

        Returns:

        """
        return self._make_query_string()

    @staticmethod
    def _execute_callback(entries: list,
                          callback: Union[Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None] = None):
        if callback:
            callback_signature = signature(callback)

            if len(callback_signature.parameters) > 1:
                raise ValueError("The callback function should have either one or zero arguments")

            elif len(callback_signature.parameters) == 1:
                callback(entries)
            else:
                callback()

    def __repr__(self):
        if isinstance(self.resource, str):
            resource = self.resource
        else:
            resource = self.resource.resource_type

        if self.query_parameters.include_parameters:
            includes = []
            rev_includes = []
            for include_param in self.query_parameters.include_parameters:
                if include_param.reverse:
                    rev_string = f"{include_param.resource}:{include_param.search_param}"
                    if include_param.target:
                        rev_string += f":{include_param.target}"
                    rev_includes.append(rev_string)
                else:
                    include_string = f"{include_param.search_param}"
                    if include_param.target:
                        include_string += f":{include_param.target}"
                    includes.append(include_string)

            include_repr = f", include={','.join(includes)}" if includes else ""
            rev_include_repr = f", reverse_includes={','.join(rev_includes)}" if rev_includes else ""
            includes_repr = include_repr + rev_include_repr
            return f"<{self.__class__.__name__}(resource={resource}{includes_repr}, url={self.query_url}>"
        else:

            return f"<{self.__class__.__name__}(resource={resource}, url={self.query_url}>"


class FHIRQuerySync(FHIRQueryBase):
    def __init__(self,
                 base_url: str,
                 resource: Union[FHIRResourceModel, fhir.resources.FHIRAbstractModel, str] = None,
                 query_parameters: FHIRQueryParameters = None,
                 auth: httpx.Auth = None,
                 headers: dict = None,
                 client: httpx.Client = None,
                 output_format: str = "json"):

        super().__init__(base_url, resource, query_parameters, auth, headers, output_format)
        if client:
            self.client = client
        else:
            self._setup_client()

    def all(self,
            page_callback: Union[Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None] = None,
            count: int = None) -> QueryResponse:
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
        return self._execute_query(page_callback=page_callback, count=count)

    def limit(self,
              n: int,
              page_callback: Union[Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None] = None,
              count: int = None) -> QueryResponse:
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
        return self._execute_query(page_callback=page_callback, count=count)

    def first(self) -> QueryResponse:
        """
        Return the first resource matching the query parameters.
        Returns:
            QueryResponse object containing the first resource matching the query

        """
        self._limit = 1
        return self._execute_query()

    def _setup_client(self):
        headers = self.headers if self.headers else {}
        headers["Content-Type"] = "application/fhir+json"
        self.client = httpx.Client(auth=self.auth, headers=headers)

    def _execute_query(self,
                       page_callback: Union[Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None] = None,
                       count: int = None) -> QueryResponse:
        r = self.client.get(self.query_url)
        r.raise_for_status()
        response = self._resolve_response_pagination(r, page_callback, count)
        return response

    def _resolve_response_pagination(
            self,
            initial_response: httpx.Response,
            page_callback: Union[Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None] = None,
            count: int = None) -> QueryResponse:

        if self.output_format == "json":
            response = self._resolve_json_pagination(initial_response, page_callback, count)

        elif self.output_format == "xml":
            response = self._resolve_xml_pagination(initial_response)
        else:
            raise ValueError(f"Unsupported output format: {self.output_format}")

        return QueryResponse(
            response=response,
            query_params=self.query_parameters,
            count=count,
            limit=self._limit,
            output_format=self.output_format,
        )

    def _resolve_json_pagination(
            self,
            initial_response: httpx.Response,
            page_callback: Union[Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None] = None,
            count: int = None) -> dict:
        response_json = initial_response.json()
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
                response_entries = response_json["entry"][:self._limit]
                response_json["entry"] = response_entries
                self._execute_callback(response_entries, page_callback)
                return response_json
            # query the linked page and add the entries to the response

            while response_json.get("link", None):
                if self._limit and len(entries) >= self._limit:
                    break
                next_page = next((link for link in response_json["link"] if link.get("relation", None) == "next"), None)
                if next_page:
                    response_json = self.client.get(next_page["url"]).json()
                    response_entries = response_json["entry"]
                    entries.extend(response_entries)
                    self._execute_callback(response_entries, page_callback)
                else:
                    break

            response_json["entry"] = entries[:self._limit] if self._limit else entries
            return response_json

    def _resolve_xml_pagination(self, server_response: httpx.Response) -> str:

        # parse the xml response and extract the initial entries
        initial_response = xmltodict.parse(server_response.text)
        entries = initial_response["Bundle"].get("entry")

        # if there are no entries, return the initial response
        if not entries:
            self.status_code = ResponseStatusCodes.NOT_FOUND
            print(f"No resources match the query - query url: {self.query_parameters.to_query_string()}")
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
                    url = url + "&_format=xml"
                    r = self.client.get(url)
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
        initial_response["Bundle"]["entry"] = entries[:self._limit] if self._limit else entries
        full_response_xml = xmltodict.unparse(initial_response, pretty=True)
        return full_response_xml


class FHIRQueryAsync(FHIRQueryBase):
    def __init__(self,
                 base_url: str,
                 resource: Union[FHIRResourceModel, fhir.resources.FHIRAbstractModel, str] = None,
                 query_parameters: FHIRQueryParameters = None,
                 auth: httpx.Auth = None,
                 headers: dict = None,
                 output_format: str = "json",
                 ):
        super().__init__(base_url, resource, query_parameters, auth, headers, output_format)

        # set up the async client instance
        self.client = None
        self._setup_client()

    async def all(self,
                  page_callback: Union[Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None] = None,
                  count: int = None) -> QueryResponse:
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

    async def limit(self,
                    n: int,
                    page_callback: Union[Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None] = None,
                    count: int = None) -> QueryResponse:
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

    def _setup_client(self):
        headers = self.headers if self.headers else {}
        headers["Content-Type"] = "application/fhir+json"
        self.client = httpx.AsyncClient(auth=self.auth, headers=headers)

    async def _execute_query(self,
                             page_callback: Union[
                                 Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None] = None,
                             count: int = None) -> QueryResponse:
        r = await self.client.get(self.query_url)
        r.raise_for_status()
        response = self._resolve_response_pagination(r, page_callback, count)
        return response

    async def _resolve_response_pagination(
            self,
            initial_response: httpx.Response,
            page_callback: Union[Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None] = None,
            count: int = None) -> QueryResponse:

        if self.output_format == "json":
            response = await self._resolve_json_pagination(initial_response, page_callback, count)

        elif self.output_format == "xml":
            response = await self._resolve_xml_pagination(initial_response)
        else:
            raise ValueError(f"Unsupported output format: {self.output_format}")

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
            page_callback: Union[Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None] = None,
            count: int = None) -> dict:
        response_json = initial_response.json()
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
                response_entries = response_json["entry"][:self._limit]
                response_json["entry"] = response_entries
                self._execute_callback(response_entries, page_callback)
                return response_json
            # query the linked page and add the entries to the response

            while response_json.get("link", None):
                if self._limit and len(entries) >= self._limit:
                    break
                next_page = next((link for link in response_json["link"] if link.get("relation", None) == "next"), None)
                if next_page:
                    response_json = await self.client.get(next_page["url"]).json()
                    response_entries = response_json["entry"]
                    entries.extend(response_entries)
                    self._execute_callback(response_entries, page_callback)
                else:
                    break

            response_json["entry"] = entries[:self._limit] if self._limit else entries
            return response_json

    def _resolve_xml_pagination(self, server_response: httpx.Response) -> str:

        # parse the xml response and extract the initial entries
        initial_response = xmltodict.parse(server_response.text)
        entries = initial_response["Bundle"].get("entry")

        # if there are no entries, return the initial response
        if not entries:
            self.status_code = ResponseStatusCodes.NOT_FOUND
            print(f"No resources match the query - query url: {self.query_parameters.to_query_string()}")
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
        initial_response["Bundle"]["entry"] = entries[:self._limit] if self._limit else entries
        full_response_xml = xmltodict.unparse(initial_response, pretty=True)
        return full_response_xml