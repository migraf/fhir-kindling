from inspect import signature
from typing import Any, Callable, List, TypeVar, Union

import fhir.resources
import httpx
from fhir.resources import FHIRAbstractModel
from fhir.resources.bundle import Bundle
from fhir.resources.fhirresourcemodel import FHIRResourceModel

from fhir_kindling.fhir_query.query_parameters import (
    FhirQueryParameters,
    FieldParameter,
    IncludeParameter,
    QueryOperators,
    ReverseChainParameter,
)
from fhir_kindling.fhir_query.query_response import (
    OutputFormats,
)

T = TypeVar("T", bound="FhirQueryBase")


class FhirQueryBase:
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
    ):
        self.base_url = base_url

        # Set up the requests session with auth and headers
        self.auth = auth
        self.headers = headers

        # initialize the resource and query parameters
        if resource:
            if isinstance(resource, str):
                self.resource = fhir.resources.get_fhir_model_class(resource)
            elif isinstance(resource, FHIRResourceModel) or isinstance(
                resource, FHIRAbstractModel
            ):
                self.resource = resource
            else:
                raise ValueError(
                    f"resource must be a FHIRResourceModel or a string, given {type(resource)}"
                )
            self.resource = self.resource.construct()
            self.query_parameters = FhirQueryParameters(
                resource=self.resource.resource_type
            )

        elif query_parameters:
            self.query_parameters = query_parameters
            self.resource = fhir.resources.get_fhir_model_class(
                query_parameters.resource
            )
            self.resource = self.resource.construct()
        else:
            raise ValueError("Either resource or query_parameters must be set")

        try:
            self.output_format = OutputFormats(output_format)
        except ValueError:
            raise ValueError(
                f"output_format must be one of {OutputFormats.__members__.keys()}"
            )
        self._includes = None
        self._limit = None
        self._count = None
        self._query_response: Union[Bundle, str, None] = None

    def where(
        self: T,
        field: str = None,
        operator: Union[QueryOperators, str] = None,
        value: Union[int, float, bool, str, list] = None,
        field_param: Union[FieldParameter, dict] = None,
    ) -> T:
        """
        Add search conditions regarding a specific field of the queried resource.
        Conditions can be added via FieldParameter class instance, via a dictionary or specifying condition via this
        method's parameter arguments (field, operator, value).
        Args:
            field_param: Instance of FieldParameter defining the field to filter for.
            field: string specifier of the field to fileter for
            operator: comparison operator either as string or QueryOperators
            value: comparison value.

        Returns:
            FhirQuery object with the added filter

        """

        # evaluate arguments
        if field_param and (field or operator or value):
            raise ValueError("Cannot use both field_param and kv parameters")
        if not field_param and not (field and operator and value):
            raise ValueError("Either field_param or kv parameters must be set")

        # create field parameters from the different argument options
        if isinstance(field_param, FieldParameter):
            added_query_param = field_param
        elif isinstance(field_param, dict):
            added_query_param = FieldParameter(**field_param)
        else:
            added_query_param = self._param_from_field(field, operator, value)

        # add the field parameter to the query parameters
        query_field_params = self.query_parameters.resource_parameters
        if isinstance(query_field_params, list) and len(query_field_params) > 0:
            query_field_params.append(added_query_param)
        else:
            query_field_params = [added_query_param]

        self.query_parameters.resource_parameters = query_field_params

        return self

    @staticmethod
    def _param_from_field(field, operator, value):
        if not (operator or operator == "") and value:
            kv_error_message = (
                f"\n\tField: {field}\n\tOperator: {operator}\n\tValue: {value}"
            )
            raise ValueError(
                f"Must provide operator and search value when using kv parameters.{kv_error_message}"
            )
        else:
            if isinstance(operator, str):
                operator = QueryOperators(operator)
            else:
                raise ValueError(
                    f"Operator must be a string or QueryOperators. Got {operator}"
                )
            added_query_param = FieldParameter(
                field=field, operator=operator, value=value
            )
        return added_query_param

    def include(
        self: T,
        resource: str = None,
        reference_param: str = None,
        target: str = None,
        reverse: bool = False,
        include_dict: dict = None,
        include_param: IncludeParameter = None,
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
            added_include_param = IncludeParameter(
                resource=resource,
                search_param=reference_param,
                target=target,
                reverse=reverse,
            )
        else:
            raise ValueError(
                "Must provide a valid instance of either include_dict or include_param or the kv parameters"
            )

        query_include_params = self.query_parameters.include_parameters
        if isinstance(query_include_params, list) and len(query_include_params) > 0:
            query_include_params.append(added_include_param)
        else:
            query_include_params = [added_include_param]

        self.query_parameters.include_parameters = query_include_params

        return self

    def has(
        self: T,
        resource: str = None,
        reference_param: str = None,
        search_param: str = None,
        operator: QueryOperators = None,
        value: Union[int, float, bool, str, list] = None,
        has_param: Union[ReverseChainParameter, dict] = None,
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
            has_param: instance of ReverseChainParameter object
        Returns:
            Updated query object with an added ReverseChainParameter

        """

        # validate method input
        if has_param and (
            resource or reference_param or search_param or operator or value
        ):
            raise ValueError("Cannot use both has_param and kv parameters")

        if not has_param and not (
            resource or reference_param or search_param or operator or value
        ):
            raise ValueError(
                "Must provide either has_param or a valid set of kv parameters"
            )

        # parse ReverseChainParameter from method input
        if isinstance(has_param, dict):
            added_has_param = ReverseChainParameter(**has_param)
        elif isinstance(has_param, ReverseChainParameter):
            added_has_param = has_param
        else:
            added_has_param = ReverseChainParameter(
                resource=resource,
                reference_param=reference_param,
                search_param=search_param,
                operator=operator,
                value=value,
            )

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
        query_string += f"&_format={self.output_format.value}"

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
        query_parameters = FhirQueryParameters.from_query_string(raw_query_string)
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
    def _execute_callback(
        entries: list,
        callback: Union[
            Callable[[List[FHIRAbstractModel]], Any], Callable[[], Any], None
        ] = None,
    ):
        if callback:
            callback_signature = signature(callback)

            if len(callback_signature.parameters) > 1:
                raise ValueError(
                    "The callback function should have either one or zero arguments"
                )

            elif len(callback_signature.parameters) == 1:
                callback(entries)
            else:
                callback()

    def __repr__(self):
        resource = self.resource.resource_type
        if self.query_parameters.include_parameters:
            includes = []
            rev_includes = []
            for include_param in self.query_parameters.include_parameters:
                if include_param.reverse:
                    rev_string = (
                        f"{include_param.resource}:{include_param.search_param}"
                    )
                    if include_param.target:
                        rev_string += f":{include_param.target}"
                    rev_includes.append(rev_string)
                else:
                    include_string = f"{include_param.search_param}"
                    if include_param.target:
                        include_string += f":{include_param.target}"
                    includes.append(include_string)

            include_repr = f", include={','.join(includes)}" if includes else ""
            rev_include_repr = (
                f", reverse_includes={','.join(rev_includes)}" if rev_includes else ""
            )
            includes_repr = include_repr + rev_include_repr
            return f"<{self.__class__.__name__}(resource={resource}{includes_repr}, url={self.query_url}>"
        else:
            return (
                f"<{self.__class__.__name__}(resource={resource}, url={self.query_url}>"
            )
