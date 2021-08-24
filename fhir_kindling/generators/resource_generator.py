import pprint
from typing import List, Union
from fhir.resources.domainresource import DomainResource
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
import os
import pendulum
from uuid import uuid4

from abc import ABC, abstractmethod


class FhirResourceGenerator:

    def __init__(self, n: int = None, resource_type: DomainResource = None):
        self.n = n
        self.resource_type = resource_type
        self.resources = None

    def generate(self, out_dir: str = None, filename: str = None):

        self.resources = self._generate()
        if out_dir:
            bundle = self.make_bundle()
            if filename:
                path = os.path.join(out_dir, filename)
            else:
                path = os.path.join(out_dir, f"bundle-{pendulum.now().isoformat()}.json")
            with open(path, "w") as bundle_file:
                bundle_file.write(bundle.json())

    @abstractmethod
    def _generate(self):
        pass

    def make_bundle(self) -> Bundle:
        entries = self._generate_bundle_entries()
        bundle_data = {
            "type": "transaction",
            "entry": entries
        }
        bundle = Bundle(**bundle_data)
        return bundle

    def _generate_bundle_entries(self):
        entries = []
        for resource in self.resources:
            bundle_entry_dict = {
                "resource": resource,
                "request": BundleEntryRequest(**{"method": "POST", "url": self.resource_type.get_resource_type()})
            }
            entry = BundleEntry(**bundle_entry_dict)
            entries.append(entry)
        return entries

    def display_schema(self):
        pprint.pprint(self.resource_type.schema())

    @staticmethod
    def generate_id():
        return str(uuid4())
