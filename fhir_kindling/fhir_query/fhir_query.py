import functools
import inspect
from typing import Union

from fhir.resources.resource import Resource
from fhir.resources import FHIRAbstractModel
import fhir.resources
import requests
import requests.auth
from pprint import pprint

from fhir.resources.patient import Patient


# def showargs_decorator(func):
#     # updates special attributes e.g. __name__,__doc__
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         # call custom inspection logic
#         inspect_decorator(func, args, kwargs)
#         # calls original function
#         func(*args, **kwargs)
#
#     # matches name of inner function
#     return wrapper
#
#
# def inspect_decorator(func, args, kwargs):
#     funcname = func.__name__
#     print("function {}()".format(funcname))
#
#     # get description of function params expected
#     argspec = inspect.getargspec(func)
#
#     # go through each position based argument
#     counter = 0
#     if argspec.args and type(argspec.args is list):
#         for arg in args:
#             # when you run past the formal positional arguments
#             try:
#                 print(str(argspec.args[counter]) + "=" + str(arg))
#                 members = inspect.getmembers(func)
#                 frame = inspect.currentframe()
#
#                 outer_frames = inspect.getouterframes(frame)
#                 print(inspect.getsource(arg))
#                 counter += 1
#             except IndexError as e:
#                 # then fallback to using the positional varargs name
#                 if argspec.varargs:
#                     varargsname = argspec.varargs
#                     print("*" + varargsname + "=" + str(arg))
#                 pass
#
#     # finally show the named varargs
#     if argspec.keywords:
#         kwargsname = argspec.keywords
#         for k, v in kwargs.items():
#             print("**" + kwargsname + " " + k + "=" + str(v))


class FHIRQuery:

    def __init__(self,
                 base_url: str,
                 resource: Union[Resource, FHIRAbstractModel, str] = None,
                 auth: requests.auth.AuthBase = None,
                 session: requests.Session = None):

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
        print(type(self.resource))

        self.resource = self.resource.construct()

        self._query_string = None
        self.conditions = None
        self._limit = None

    def where(self, *filter_args):
        # todo evaluate arbitrary number of expressions based on fields of the resource and query values
        conditions = self._evaluate_conditions(filter_args)
        return self

    def _setup_session(self):
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Content-Type": "application/fhir+json"})

    def _evaluate_conditions(self, filter_args):
        outer_frames = inspect.getouterframes(inspect.currentframe())
        print(outer_frames)

    def include(self):
        pass

    def has(self):
        pass

    def all(self):
        self._limit = None
        # todo execute the pre built query string and return all resources that match the query
        results = self._query_server()
        return results

    def limit(self, n: int):
        self._limit = n
        return self._query_server()

    def first(self):
        self._limit = 1
        return self._query_server()

    def set_query_string(self, query_string: str):
        self._query_string = query_string

    @property
    def query_url(self):

        if not self._query_string:
            self._make_query_string()
        return self._query_string

    def _query_server(self):
        r = self.session.get(self.query_url)
        r.raise_for_status()

        full_response = self._resolve_response_pagination(r)
        return full_response

    def _resolve_response_pagination(self, server_response: requests.Response):
        # todo outsource into search response class
        response = server_response.json()
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

    def _make_query_string(self):
        query_string = self.base_url + "/" + self.resource.get_resource_type() + "?"

        if self.conditions:
            # todo
            pass

        # todo include and has
        if self._limit:
            query_string += f"_count={self._limit}"
        else:
            query_string += f"_count=5000"

        query_string += "&_format=json"

        print(query_string)
        self._query_string = query_string


if __name__ == '__main__':
    query = FHIRQuery("test", "Patient")

    patient = Patient.construct()
    print(inspect.signature(Patient))
    filter = query.where(
        patient.name == "John",
        patient.address in ["Germany"])
