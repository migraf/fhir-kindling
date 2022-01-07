from pydantic import BaseModel
from enum import Enum
from typing import Union, Optional, List


class QueryOperators(str, Enum):
    """
    Enumeration of query operators.
    """
    eq = "$eq"
    ne = "$ne"
    gt = "$gt"
    lt = "$lt"
    ge = "$ge"
    le = "$le"
    sa = "$sa"
    eb = "$eb"
    in_ = "$in"
    not_in = "$not_in"
    contains = "$contains"
    regex = "$regex"


class QueryParameter(BaseModel):
    """
    Base class for query parameters.
    """

    def to_url_param(self) -> str:
        """
        Convert the query parameter to a URL parameter.
        """
        raise NotImplementedError()


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
        pass



class ReverseChainParameter(QueryParameter):
    """
    Class to represent reverse chain parameters in a fhir query for querying resources based on properties of other
    resources that refer to them.
    """
    resource: str
    reference_param: str
    search_param: str
    query_operator: QueryOperators = QueryOperators.eq
    search_value: Union[str, int, float, list]

    def to_url_param(self) -> str:
        pass


class FieldParameter(QueryParameter):
    """
    The Field Query Parameter class.
    """
    field: str
    operator: QueryOperators
    value: Union[str, int, float, list]

    def to_url_param(self) -> str:
        pass


class FHIRQueryParameters(BaseModel):
    """
    Collection of query parameters for a fhir query.
    """
    resource: str
    resource_parameters: Optional[List[FieldParameter]] = None
    include_parameters: Optional[List[IncludeParameter]] = None
    has_parameters: Optional[List[QueryParameter]] = None

    def to_query_string(self):
        pass

    def from_query_string(self):
        pass
