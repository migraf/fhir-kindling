import collections
import json
import pathlib
from typing import Union

from fhir.resources.bundle import Bundle
from requests import Session, Response
import xmltodict


class QueryResponse:

    def __init__(self, session: Session, response: Response, format: str = "json", limit: int = None):
        self.session = session
        self.format = format
        self._limit = limit
        self.response = self.process_server_response(response)

    def process_server_response(self, response: Response):
        if self.format in ["json", "dict"]:
            return self._resolve_json_pagination(response)
        elif self.format == "xml":
            return self._resolve_xml_pagination(response)

        elif self.format == "bundle":
            json_bundle = self._resolve_json_pagination(response)
            return Bundle(**json_bundle)

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

    def _resolve_xml_pagination(self, server_response: Response) -> str:

        initial_response = xmltodict.parse(server_response.text)
        entries = initial_response["Bundle"]["entry"]
        response = initial_response
        while True:
            next_page = False
            for link in response["Bundle"]["link"]:
                if isinstance(link, collections.OrderedDict):
                    relation_dict = dict(link["relation"])
                else:
                    break
                if relation_dict.get("@value") == "next":
                    print("Getting next")
                    # get url and extend with xml format
                    url = link["url"]["@value"]
                    url = url + "&_format=xml"
                    r = self.session.get(url)
                    r.raise_for_status()
                    response = xmltodict.parse(r.text)
                    added_entries = response["Bundle"]["entry"]
                    entries.extend(added_entries)
                    # Stop resolving the pagination when the limit is reached
                    if self._limit:
                        if len(entries) >= self._limit:
                            next_page = False
                        else:
                            next_page = True
                    else:
                        next_page = True

            if not next_page:
                print("All pages found")
                break
        # added the paginated resources to the initial response
        initial_response["Bundle"]["entry"] = entries[:self._limit] if self._limit else entries
        full_response_xml = xmltodict.unparse(initial_response, pretty=True)
        return full_response_xml

    @property
    def resources(self):
        if self.format == "xml":
            raise NotImplementedError("Resource parsing not supported for xml format")

    def to_file(self, file_path: Union[str, pathlib.Path]):

        with open(file_path, "w") as f:
            if self.format == "xml":
                f.write(self.response)

            elif self.format == "json":
                json.dump(self.response, f, indent=2)

            elif self.format in ["dict", "bundle"]:
                print("Storing as json")
                if isinstance(self.response, Bundle):
                    json.dump(self.response.dict(), f, indent=2)
                else:
                    json.dump(self.response, f)
