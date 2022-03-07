from typing import Union
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle
from fhir.resources.fhirresourcemodel import FHIRResourceModel
import fhir.resources
import requests
import requests.auth

from fhir_kindling.fhir_query.query_response import QueryResponse
from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters, IncludeParameter, FieldParameter, \
    ReverseChainParameter, QueryOperators


class FHIRQuery:
    def __init__(self,
                 base_url: str,
                 resource: Union[FHIRResourceModel, fhir.resources.FHIRAbstractModel, str] = None,
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

    def include(self,
                resource: str = None,
                reference_param: str = None,
                target: str = None,
                reverse: bool = False,
                include_dict: dict = None,
                include_param: IncludeParameter = None
                ) -> 'FHIRQuery':

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

    def has(self,
            resource: str = None,
            reference_param: str = None,
            search_param: str = None,
            operator: QueryOperators = None,
            value: Union[int, float, bool, str, list] = None,
            has_param_dict: dict = None,
            has_param: ReverseChainParameter = None
            ) -> 'FHIRQuery':
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

    def all(self):
        """
        Execute the query and return all results matching the query parameters.
        Returns:
            QueryResponse object containing all resources matching the query, as well os optional included
            resources.

        """
        self._limit = None
        return self._execute_query()

    def limit(self, n: int):
        """
        Execute the query and return the first n results matching the query parameters.
        Args:
            n: number of resources to return

        Returns:
            QueryResponse object containing the first n resources matching the query, as well os optional included
            resources.

        """
        self._limit = n
        return self._execute_query()

    def first(self):
        """
        Return the first resource matching the query parameters.
        Returns:
            QueryResponse object containing the first resource matching the query

        """
        self._limit = 1
        return self._execute_query()

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

    def _setup_session(self):
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Content-Type": "application/fhir+json"})

    def _execute_query(self):
        r = self.session.get(self.query_url)
        r.raise_for_status()
        response = QueryResponse(
            session=self.session,
            response=r,
            query_params=self.query_parameters,
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
            return f"<FHIRQuery(resource={resource}{includes_repr}, url={self.query_url}>"
        else:

            return f"<FHIRQuery(resource={resource}, url={self.query_url}>"
