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
                 resource: Union[Resource, fhir.resources.FHIRAbstractModel, str] = None,
                 query_parameters: FHIRQueryParameters = None,
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
        self._includes = None
        self._limit = None
        self._count = count
        self._query_response: Union[Bundle, str] = None
        if query_parameters:
            self.query_parameters = query_parameters
        else:
            self.query_parameters: FHIRQueryParameters = FHIRQueryParameters(resource=self.resource.resource_type)

    def where(self,
              field: str = None,
              operator: Union[QueryOperators, str] = None,
              value: Union[int, float, bool, str, list] = None,
              field_param: FieldParameter = None,
              filter_dict: dict = None
              ) -> 'FHIRQuery':
        """
        Add search conditions regarding a specific field of the queried resource.
        Conditions can be added via FieldParmeter class instance, via a dictionary or specifying condition via this
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
            if not (operator or operator is "") and value:
                kv_error_message = f"\n\tField: {field}\n\tOperator: {operator}\n\tValue: {value}"
                raise ValueError(f"Must provide operator and search value when using kv parameters.{kv_error_message}")
            else:

                if isinstance(operator, str):
                    operator = QueryOperators(operator)
                if isinstance(operator, QueryOperators):
                    print(f"Operator: {operator}")
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
        return self._execute_query()

    def first(self):
        self._limit = 1
        return self._execute_query()

    def set_query_string(self, raw_query_string: str):
        # todo parse query string into conditions
        query_parameters = FHIRQueryParameters.from_query_string(raw_query_string)
        self.query_parameters = query_parameters

    @property
    def query_url(self):
        return self._make_query_string()

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
                                 limit=self._limit
                                 )
        return response

    def _make_query_string(self):
        query_string = f"{self.base_url}{self.query_parameters.to_query_string()}"
        if self._limit:
            query_string += f"&_count={self._limit}"
        else:
            query_string += f"&_count={self._count}"
        query_string += f"&_format={self.output_format}"

        return query_string
