from pydantic import BaseModel, validator
from enum import Enum
from typing import Union, Optional, List


class QueryOperators(str, Enum):
    """
    Enumeration of query operators.
    """
    eq = ""
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
    def from_url_param(cls, url_string: str) -> "QueryParameter":
        """
        Create a query parameter object from an url query snippet
        """
        raise NotImplementedError()

    @staticmethod
    def check_url_param_primitives(value: str) -> Union[int, float, bool, str]:
        """
        Check if the string

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
        target = f"&{self.target}" if self.target else ""
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
        resource, search_param = param.split(":")

        param_split = search_param.split("&")
        if len(param_split) == 2:
            target = param_split[1]
            search_param = param_split[0]
        else:
            target = None
            search_param = param_split[0]

        return cls(
            resource=resource,
            search_param=search_param,
            target=target,
            iterate=iterate,
            reverse=reverse
        )


class ReverseChainParameter(QueryParameter):
    """
    Class to represent reverse chain parameters in a fhir query for querying resources based on properties of other
    resources that refer to them.
    """
    resource: str
    reference_param: str
    search_param: str
    query_operator: QueryOperators = QueryOperators.eq
    value: Union[int, float, list, bool, str]

    class Config:
        smart_union = True

    def to_url_param(self) -> str:
        pass

    @classmethod
    def from_url_param(cls, url_string: str) -> "ReverseChainParameter":
        pass


class FieldParameter(QueryParameter):
    """
    The Field Query Parameter class.
    """
    field: str
    operator: QueryOperators
    value: Union[int, float, list, bool, str]

    class Config:
        smart_union = True

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

    def to_url_param(self) -> str:
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

        url_param = f"{self.field}={operator_prefix}{query_value}"

        return url_param

    @classmethod
    def from_url_param(cls, url_string: str) -> "FieldParameter":
        field, param = url_string.split("=")

        try:
            operator = QueryOperators(param[:2])
            value = param[2:]
            if operator == QueryOperators.ne and "," in value:
                value = [cls.check_url_param_primitives(v) for v in value.split(",")]
            else:
                value = cls.check_url_param_primitives(value)

        except ValueError:
            value = param
            if "," in value:
                operator = QueryOperators.in_
                value = [cls.check_url_param_primitives(v) for v in value.split(",")]
            else:
                operator = QueryOperators.eq
                value = cls.check_url_param_primitives(value)

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
    has_parameters: Optional[List[QueryParameter]] = None

    def to_query_string(self) -> str:
        pass

    @classmethod
    def from_query_string(cls, query_string: str) -> "FHIRQueryParameters":
        pass
