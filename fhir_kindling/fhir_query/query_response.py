from requests import Session, Response
from lxml import etree as et
import xmltodict


class QueryResponse:

    def __init__(self, session: Session, response: Response, format: str = "json", limit: int = None):
        self.session = session
        self.format = format
        self._limit = limit
        self.response = self.process_server_response(response)

    def process_server_response(self, response: Response):
        if self.format == "json":
            return self._resolve_json_pagination(response)
        elif self.format == "xml":
            return self._resolve_xml_pagination(response)

    def _resolve_json_pagination(self, server_response: Response):
        response = server_response.json()
        link = response.get("link", None)
        if not link:
            return response
        else:
            print("Resolving response pagination")
            entries = []
            entries.extend(response["entry"])

            if self._limit:
                if len(entries) >= self._limit:
                    response["entry"] = response["entry"][:self._limit]
                    return response

            while response.get("link", None):

                if self._limit and len(entries) >= self._limit:
                    print("Limit reached stopping pagination resolve")
                    break

                next_page = next((link for link in response["link"] if link.get("relation", None) == "next"), None)
                if next_page:
                    response = self.session.get(next_page["url"]).json()
                    entries.extend(response["entry"])
                else:
                    break

            response["entry"] = entries[:self._limit] if self._limit else entries
            return response

    def _resolve_xml_pagination(self, server_response: Response):
        response_dict = xmltodict.parse(server_response.text)
        print(response_dict["Bundle"]["link"])



    @property
    def resources(self):
        return self.response["entry"]

    def to_json(self):
        pass

    def to_xml(self):
        pass
