import json
from typing import Union, List
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle
from fhir.resources.fhirtypes import ResourceType
import fhir.resources
import requests
import requests.auth

from fhir_kindling.fhir_query.query_response import QueryResponse
from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters, IncludeParameter, FieldParameter, \
    ReverseChainParameter, QueryOperators, parse_parameter_value


class FHIRQuery:

    def __init__(self,
                 base_url: str,
                 resource: Union[Resource, fhir.resources.FHIRAbstractModel, str],
                 auth: requests.auth.AuthBase = None,
                 session: requests.Session = None,
                 output_format: str = "json",
                 count: int = 5000):

        self.base_url = base_url

        # Set up the requests session with auth and headers
        self.auth = auth
        if session:
            self.session = session
        else:
            self._setup_session()

        # initialize the resource
        if isinstance(resource, str):
            self.resource = fhir.resources.get_fhir_model_class(resource)
        else:
            self.resource = resource

        self.resource = self.resource.construct()
        if not self.resource:
            raise ValueError(f"No valid resource given: {resource}")
        self.output_format = output_format
        self._query_string = None
        self._includes = None
        self.conditions = None
        self._limit = None
        self._count = count
        self._query_response: Union[Bundle, str] = None
        self.query_parameters: FHIRQueryParameters = FHIRQueryParameters(resource=self.resource.resource_type)

    def with_params(self, query_parameters: FHIRQueryParameters):
        self.query_parameters = query_parameters

    def where(self,
              field_param: FieldParameter = None,
              filter_dict: dict = None,
              field: str = None,
              operator: Union[QueryOperators, str] = None,
              value: Union[int, float, bool, str, list] = None
              ) -> 'FHIRQuery':

        # evaluate arguments
        if field_param and filter_dict:
            raise ValueError("Cannot use both field_param and filter_dict")
        elif field_param and field and operator and value:
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
            if not operator and value:
                kv_error_message = f"\n\tField: {field}\n\tOperator: {operator}\n\tValue: {value}"
                raise ValueError(f"Must provide operator and search value when using kv parameters.{kv_error_message}")
            else:
                if isinstance(operator, str):
                    operator = QueryOperators(operator)
                elif isinstance(operator, QueryOperators):
                    pass
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

    def include(self, include_resource: Union[Resource, fhir.resources.FHIRAbstractModel, str, ResourceType],
                param: str = None,
                reverse: bool = False):

        if self._includes is None:
            self._includes = []
        if isinstance(include_resource, str):
            try:
                resource = fhir.resources.get_fhir_model_class(include_resource)
                resource_name = resource.get_resource_type()
            except KeyError as e:
                raise ValueError(f"Invalid resource type: {include_resource} \n {e}")
        else:
            resource_name = include_resource.get_resource_type()
        include_param = IncludeParameter(resource=resource_name, search_param=param, reverse=reverse)
        self._includes.append(include_param)
        return self

    def has(self, resource: Union[Resource, fhir.resources.FHIRAbstractModel, str], condition: str = None):
        pass

    def all(self):
        self._limit = None
        return self._execute_query()

    def limit(self, n: int):
        self._limit = n
        self._execute_query()
        return self._execute_query()

    def first(self):
        self._limit = 1
        return self._execute_query()

    def set_query_string(self, raw_query_string: str):
        # todo parse query string into conditions
        validated_string = self._validate_raw_query_string(raw_query_string)
        self._query_string = self.base_url + validated_string

    @property
    def query_url(self):
        if not self._query_string:
            self._make_query_string()
        return self._query_string

    def _setup_session(self):
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Content-Type": "application/fhir+json"})

    def _execute_query(self):
        r = self.session.get(self.query_url)
        r.raise_for_status()
        included_resources = [include.resource for include in self._includes] if self._includes else None
        response = QueryResponse(self.session,
                                 response=r,
                                 resource=self.resource.get_resource_type(),
                                 included_resources=included_resources,
                                 output_format=self.output_format,
                                 limit=self._limit)
        return response

    def _make_query_string(self):
        query_string = self.base_url + "/" + self.resource.get_resource_type() + "?"

        if self.conditions:
            query_string += self.conditions
        if self._includes:
            for include in self._includes:
                query_string += f"&{include.query_string()}"

        # todo implement has / reverse chaining
        if self._limit:
            query_string += f"&_count={self._limit}"
        else:
            query_string += f"&_count={self._count}"

        # todo improve xml support with full parser
        query_string += f"&_format={self.output_format}"
        self._query_string = query_string

    def _validate_raw_query_string(self, raw_query_string: str) -> str:
        if self.output_format == "xml":
            if "&_format=json" in raw_query_string:
                return raw_query_string.replace("&_format=json", "&_format=xml")
            if "&_format=xml" not in raw_query_string:
                return raw_query_string + "&_format=xml"
        if self.output_format in ["json", "dict", "bundle"]:
            if "&_format=xml" in raw_query_string:
                return raw_query_string.replace("&_format=xml", "")
            else:
                return raw_query_string

    def process_query_parameters(self):
        pass

    def _parse_filter_dict(self, filter_dict: dict) -> str:
        # todo validate the query with the fields of the selected model
        query_params = []
        for key, value in filter_dict.items():
            query_param = f"{key}={value}"
            query_params.append(query_param)

        query_string = "&".join(query_params)
        return query_string

    def _serialize_output(self):
        if isinstance(self._query_response, bytes):
            self._query_response = self._query_response.decode("utf-8")
        if isinstance(self._query_response, str):
            if self.output_format == "xml":
                return self._query_response
            elif self.output_format == "json":
                return Bundle.construct(**json.loads(self._query_response)).json()
            elif self.output_format == "dict":
                return Bundle.construct(**json.loads(self._query_response)).dict()
            elif self.output_format == "model":
                return Bundle.construct(**json.loads(self._query_response))

        elif isinstance(self._query_response, Bundle):
            if self.output_format == "json":
                return self._query_response.json(indent=2)
            elif self.output_format == "dict":
                return self._query_response.dict()
            elif self.output_format == "model":
                return self._query_response

        else:
            raise ValueError("Unable to serialize query response")
