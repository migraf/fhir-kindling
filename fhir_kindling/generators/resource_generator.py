import math
import pprint
from typing import List, Union
from fhir.resources.domainresource import DomainResource
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.reference import Reference
import os
import pendulum
from uuid import uuid4

from abc import ABC, abstractmethod

from fhir.resources.resource import Resource


class FhirResourceGenerator:

    def __init__(self, n: int = None, n_per_patient: int = 1, resource_type: DomainResource = None):
        self._patient_references = None
        self.n = n
        self.resource_type = resource_type
        self.resources = None
        self.n_per_patient = n_per_patient

    @property
    def num_patients(self):
        return math.ceil(self.n/self.n_per_patient)

    def generate(self, out_dir: str = None, filename: str = None, generate_ids: bool = False,
                 patient_references: List[Reference] = None) -> List[Resource]:
        self._patient_references = patient_references
        self.resources = self._generate()
        if generate_ids:
            for resource in self.resources:
                resource.id = self.generate_id()

        if self._patient_references:
            self.update_with_patient_ids()

        if out_dir:
            bundle = self.make_bundle()
            if filename:
                path = os.path.join(out_dir, filename)
            else:
                path = os.path.join(out_dir, f"bundle-{pendulum.now().to_date_string()}.json")
            with open(path, "w") as bundle_file:
                bundle_file.write(bundle.json())
        return self.resources

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

    def update_with_patient_ids(self):
        # Step with n per patient
        for index in range(0, len(self.resources), self.n_per_patient):
            patient_resources = self.resources[index: index + self.n_per_patient]
            for resource in patient_resources:
                resource.patient = {
                    "reference": self._patient_references[int(index / self.n_per_patient)],
                    "type": "Patient"
                }

        print(self.resources)

    def display_schema(self):
        pprint.pprint(self.resource_type.schema())

    @staticmethod
    def generate_id():
        return str(uuid4())
