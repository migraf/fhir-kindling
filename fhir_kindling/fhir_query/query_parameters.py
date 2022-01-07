from pydantic import BaseModel
from enum import Enum
from typing import Union, Optional, List


class QueryOperators(str, Enum):
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


class IncludeParameter(BaseModel):
    """
    Class to represent include parameters in a fhir query
    """
    resource: str
    search_param: str
    target: Optional[str] = None
    reverse: bool = False
    iterate: bool = False


class ReverseChainParameter(BaseModel):
    """
    Class to represent reverse chain parameters in a fhir query for querying resources based on properties of other
    resources that refer to them.
    """
    resource: str
    reference_param: str
    search_param: str
    query_operator: QueryOperators = QueryOperators.eq
    search_value: Union[str, int, float, list]


class FieldQueryParameter(BaseModel):
    """
    The Field Query Parameter class.
    """
    operator: QueryOperators
    value: Union[str, int, float, list]


class QueryParameter(BaseModel):
    """
    The Query Parameter class.
    """
    field: str
    field_query: Union[List[FieldQueryParameter], FieldQueryParameter]


class FHIRQueryParameters(BaseModel):
    resource: str
    resource_parameters: Optional[List[QueryParameter]] = None
    include_parameters: Optional[List[IncludeParameter]] = None
    has_parameters: Optional[List[QueryParameter]] = None
