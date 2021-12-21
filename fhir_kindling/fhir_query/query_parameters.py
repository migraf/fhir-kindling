from dataclasses import dataclass


@dataclass
class IncludeParam:
    resource: str
    search_param: str
    reverse: bool = False
    type: str = None

    def query_string(self) -> str:
        include_type = '_revinclude' if self.reverse else '_include'
        query_string = f'{include_type}={self.resource}:{self.search_param}'
        if self.type:
            query_string += f':{self.type}'
        return query_string



