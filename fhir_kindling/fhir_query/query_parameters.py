import attr
from typing import Union, List


@attr.s
class QueryParameter(object):
    variable: str = attr.ib()
    condition: Union[str, List[str]] = attr.ib()

    @classmethod
    def from_segment(cls, str):
        pass

