import functools
import inspect
import json
import os
from typing import Union, List

from dotenv import load_dotenv, find_dotenv
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle
import fhir.resources
import requests
import requests.auth
import xml.etree.ElementTree as ET


class FHIRQuery:

    def __init__(self,
                 base_url: str,
                 resource: Union[Resource, fhir.resources.FHIRAbstractModel, str] = None,
                 auth: requests.auth.AuthBase = None,
                 session: requests.Session = None,
                 output_format: str = "json"):

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
        self._query_string = None
        self.conditions: List[str] = []
        self._limit = None
        self._query_response: Union[Bundle, str] = None

    def where(self, filter_dict: dict = None):
        # todo evaluate arbitrary number of expressions based on fields of the resource and query values
        self._parse_filter_dict(filter_dict)
        return self

    def _setup_session(self):
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Content-Type": "application/fhir+json"})

    def include(self):
        pass

    def has(self):
        pass

    def all(self):
        self._limit = None
        self._execute_query()
        return self._serialize_output()

    def limit(self, n: int):
        self._limit = n
        self._execute_query()
        return self._serialize_output()

    def first(self):
        self._limit = 1
        self._execute_query()
        return self._serialize_output()

    def set_query_string(self, raw_query_string: str):
        self._query_string = self.base_url + raw_query_string

    @property
    def query_url(self):
        if not self._query_string:
            self._make_query_string()
        return self._query_string

    def _execute_query(self):
        r = self.session.get(self.query_url)
        r.raise_for_status()
        if self.output_format == "xml":
            self._query_response = r.content
        else:
            response = self._resolve_response_pagination(r)
            self._query_response = Bundle(**response)

    def _resolve_response_pagination(self, server_response: requests.Response):
        # todo outsource into search response class
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
            # remove next linked from resolved pagination
            return response

    def _make_query_string(self):
        query_string = self.base_url + "/" + self.resource.get_resource_type() + "?"

        if self.conditions:
            # todo
            pass
        # todo implement include and has
        if self._limit:
            query_string += f"_count={self._limit}"
        else:
            query_string += f"_count=5000"

        # todo improve xml support with full parser
        if self.output_format == "xml":
            query_string += f"&_format=xml"
        else:
            query_string += f"&_format=json"

        self._query_string = query_string

    def _parse_filter_dict(self, filter_dict: dict):
        pass

    def _serialize_output(self):
        # TODO improve the super super basic xml support
        if isinstance(self._query_response, bytes):
            self._query_response = self._query_response.decode("utf-8")
        if isinstance(self._query_response, str):
            if self.output_format == "xml":
                return self._query_response
            elif self.output_format == "json":
                return Bundle.construct(**json.loads(self._query_response)).json()
            elif self.output_format == "dict":
                return Bundle.construct(**json.loads(self._query_response)).dict()
            elif self.output_format == "model":
                return Bundle.construct(**json.loads(self._query_response))

        elif isinstance(self._query_response, Bundle):
            if self.output_format == "json":
                return self._query_response.json(indent=2)
            elif self.output_format == "dict":
                return self._query_response.dict()
            elif self.output_format == "model":
                return self._query_response

        else:
            raise ValueError("Unable to serialize query response")
