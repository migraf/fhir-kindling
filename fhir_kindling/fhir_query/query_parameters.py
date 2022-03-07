from abc import ABC

from pydantic import BaseModel, validator, root_validator
from enum import Enum
from typing import Union, Optional, List, Tuple

from fhir_kindling.util.resources import valid_resource_name


class QueryOperators(str, Enum):
    """
    Enumeration of query operators.
    """
    eq = "eq"
    ne = "ne"
    gt = "gt"
    lt = "lt"
    ge = "ge"
    le = "le"
    sa = "sa"
    eb = "eb"
    in_ = "in"
    not_in = "not_in"
    contains = "contains"
    regex = "regex"


"""
utility functions for parsing query parameters and values
"""


def check_url_param_primitives(value: str) -> Union[int, float, bool, str]:
    """
    Check if the string contains other primitives and return them before finally returning the string.

    Args:
        value: string of the value to check

    Returns:
        The value if it is a primitive type, otherwise return string.
    """
    if value.lower() == "true" or value.lower() == "false":
        return value.lower() == "true"
    # parsing order matters for ints and floats
    try:
        value = int(value)
        return value
    except ValueError:
        pass
    try:
        value = float(value)
        return value
    except ValueError:
        pass

    return value


def parse_parameter_value(url_value: str) -> Tuple[QueryOperators, Union[int, float, bool, str, list]]:
    """
    Parse a query parameter value for operators and value types

    Args:
        url_value: string snippet of the query url (after =)

    Returns: Tuple of the operator and the value

    """
    try:
        operator = QueryOperators(url_value[:2])
        value = url_value[2:]
        if operator == QueryOperators.ne and "," in value:
            value = [check_url_param_primitives(v) for v in value.split(",")]
            operator = QueryOperators.not_in
        else:
            value = check_url_param_primitives(value)

    except ValueError:
        value = url_value
        if "," in value:
            operator = QueryOperators.in_
            value = [check_url_param_primitives(v) for v in value.split(",")]
        else:
            operator = QueryOperators.eq
            value = check_url_param_primitives(value)
    return operator, value


class QueryParameter(BaseModel):
    """
    Base class for query parameters.
    """

    def to_url_param(self) -> str:
        """
        Convert the query parameter to a URL parameter.
        """
        raise NotImplementedError()

    @classmethod
    def from_url_param(cls, url_string: str):
        """
        Create a query parameter object from an url query snippet
        """
        raise NotImplementedError()


class QuerySearchParameter(QueryParameter, ABC):
    operator: QueryOperators
    value: Union[int, float, bool, str, list]

    @validator("value")
    def check_value(cls, v, values):
        if isinstance(v, list):
            if values["operator"] not in [QueryOperators.in_, QueryOperators.not_in]:
                raise ValueError(
                    "List values can only be used with the 'in' and 'not_in' operator."
                )
            for item in v:
                if not isinstance(item, (str, int, float, bool)):
                    raise ValueError(f"Invalid value type: {type(item)}")
        else:
            if values.get("operator") in [QueryOperators.in_, QueryOperators.not_in]:
                raise ValueError("The 'in' and 'not_in' operators can only be used with a list value.")

        return v

    def make_search_parameter_values(self) -> Tuple[str, str]:
        if self.operator in [QueryOperators.eq, QueryOperators.in_]:
            operator_prefix = ""
        else:
            operator_prefix = self.operator.value
        if isinstance(self.value, list):
            query_value = ",".join(self.value)
        elif isinstance(self.value, bool):
            query_value = str(self.value).lower()
        else:
            query_value = self.value

        return operator_prefix, query_value


class IncludeParameter(QueryParameter):
    """
    Class to represent include parameters in a fhir query
    """

    resource: str
    search_param: str
    target: Optional[str] = None
    reverse: bool = False
    iterate: bool = False

    def to_url_param(self) -> str:
        query_param = "_include" if not self.reverse else "_revinclude"

        iterate = ":iterate" if self.iterate else ""
        target = f":{self.target}" if self.target else ""
        url_param = f"{query_param}{iterate}={self.resource}:{self.search_param}{target}"
        return url_param

    @classmethod
    def from_url_param(cls, url_string: str) -> "IncludeParameter":
        field, param = url_string.split("=")
        split_field = field.split(":")
        if len(split_field) == 2:
            reverse = split_field[0] == "_revinclude"
            iterate = split_field[1] == "iterate"
            if not iterate:
                raise ValueError(
                    f"Invalid include iterate parameter in: {url_string}\n\t {field} must contain ':iterate'")
        else:
            reverse = split_field[0] == "_revinclude"
            iterate = False
        param_fields = param.split(":")

        if len(param_fields) == 2:
            resource, search_param = param_fields
            target = None
        elif len(param_fields) == 3:
            resource, search_param, target = param_fields
        else:
            raise ValueError(f"Too many fields in include parameter: {url_string} - "
                             f"<resource>:<search_param> or <resource>:<search_param>:<target>")

        return cls(
            resource=resource,
            search_param=search_param,
            target=target,
            iterate=iterate,
            reverse=reverse
        )


class ReverseChainParameter(QuerySearchParameter):
    """
    Class to represent reverse chain parameters in a fhir query for querying resources based on properties of other
    resources that refer to them.
    """
    resource: str
    reference_param: str
    search_param: str
    operator: QueryOperators
    value: Union[int, float, list, bool, str]

    _normalize_resource = validator("resource", allow_reuse=True)(valid_resource_name)

    class Config:
        smart_union = True

    def to_url_param(self) -> str:
        operator_prefix, query_value = self.make_search_parameter_values()
        url_param = f"_has:{self.resource}:{self.reference_param}:{self.search_param}={operator_prefix}{query_value}"

        return url_param

    @classmethod
    def from_url_param(cls, url_string: str) -> "ReverseChainParameter":
        chained_field, param = url_string.split("=")
        _, resource, reference_param, search_param = chained_field.split(":")
        operator, value = parse_parameter_value(url_value=param)
        return cls(
            resource=resource,
            reference_param=reference_param,
            search_param=search_param,
            operator=operator,
            value=value
        )


class FieldParameter(QuerySearchParameter):
    """
    The Field Query Parameter class.
    """
    field: str

    class Config:
        smart_union = True

    def to_url_param(self) -> str:
        operator_prefix, query_value = self.make_search_parameter_values()

        url_param = f"{self.field}={operator_prefix}{query_value}"

        return url_param

    @classmethod
    def from_url_param(cls, url_string: str) -> "FieldParameter":
        field, param = url_string.split("=")
        operator, value = parse_parameter_value(url_value=param)
        return FieldParameter(
            field=field,
            operator=operator,
            value=value
        )


class FHIRQueryParameters(BaseModel):
    """
    Collection of query parameters for a fhir query.
    """
    resource: str
    resource_parameters: Optional[List[FieldParameter]] = None
    include_parameters: Optional[List[IncludeParameter]] = None
    has_parameters: Optional[List[ReverseChainParameter]] = None

    _normalize_resource = validator("resource", allow_reuse=True)(valid_resource_name)

    @root_validator
    def validate_parameters(cls, values):
        # todo
        return values

    def to_query_string(self) -> str:
        """
        Converts the parameters to a query string that can be used with a fhir server's REST API
        Returns:
        """
        query_string = f"/{self.resource}?"
        if self.resource_parameters:
            resource_url_params = "&".join([param.to_url_param() for param in self.resource_parameters])
            query_string += resource_url_params
        # include parameters
        if self.include_parameters:
            if self.resource_parameters:
                query_string += "&"
            include_url_params = "&".join([param.to_url_param() for param in self.include_parameters])
            query_string += include_url_params
        # reverse chain parameters
        if self.has_parameters:
            if self.resource_parameters or self.include_parameters:
                query_string += "&"
            has_url_params = "&".join([param.to_url_param() for param in self.has_parameters])
            query_string += has_url_params

        return query_string

    @classmethod
    def from_query_string(cls, query_string: str) -> "FHIRQueryParameters":

        # split resource and query parameters
        resource, query = query_string.split("?")

        # clean up and validate resource
        if resource[0] == "/":
            resource = resource[1:]
        resource = valid_resource_name(resource)

        resource_parameters = None
        include_parameters = None
        has_parameters = None
        if query:
            # parse query parameters
            query_params = query.split("&")
            resource_parameters = []
            include_parameters = []
            has_parameters = []
            for param in query_params:
                # start with the special keywords and finally attempt to parse as resource query
                if param.startswith("_has"):
                    has_param = ReverseChainParameter.from_url_param(param)
                    has_parameters.append(has_param)
                elif param.startswith("_include") or param.startswith("_revinclude"):
                    include_param = IncludeParameter.from_url_param(param)
                    include_parameters.append(include_param)
                else:
                    resource_param = FieldParameter.from_url_param(param)
                    resource_parameters.append(resource_param)

        return cls(
            resource=resource,
            resource_parameters=resource_parameters,
            include_parameters=include_parameters,
            has_parameters=has_parameters
        )
