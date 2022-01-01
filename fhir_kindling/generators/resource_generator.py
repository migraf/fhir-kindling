import math
import pprint
from typing import List, Union, Type, Callable
from fhir.resources.domainresource import DomainResource
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.reference import Reference
from fhir.resources.fhirtypes import AbstractBaseType, AbstractType
from fhir.resources import get_fhir_model_class, FHIRAbstractModel
import os
import pendulum
from uuid import uuid4
from abc import abstractmethod
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
        return math.ceil(self.n / self.n_per_patient)

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
    def _generate(self) -> List[Resource]:
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


class ResourceGenerator:

    def __init__(self, resource: str, n: int, field_values: dict = None, disable_validation: bool = False):
        self.resource = get_fhir_model_class(resource)
        self.field_values = field_values
        self._check_required_fields()
        self.disable_validation = disable_validation
        self.n = n

    def required_fields(self) -> List[str]:
        required_fields = []
        for field_name, field in self.resource.__fields__.items():
            if field.required:
                required_fields.append(field_name)
        return required_fields

    def fields(self):
        return self.resource.__fields__

    def generate(self):
        if not self.disable_validation:
            self._check_required_fields()
        resources = self._generate_resources()
        return resources

    def _generate_resources(self):
        resources = []
        for i in range(self.n):
            resource = self._generate_resource()
            resources.append(resource)
        return resources

    def _generate_resource(self):
        resource = self.resource.construct()
        for field_name, field_value in self.field_values.items():
            self._generate_field_value(resource, field_name, field_value)

        return resource

    def _generate_field_value(self, resource: Resource, field_name: str,
                              field_value: Union[dict, str, int, float, list, Callable]):
        if isinstance(field_value, dict):
            value = self._generate_resource_value_from_dict(resource, field_name, field_value)
        elif isinstance(field_value, list):
            value = self._generate_resource_value_from_list(resource, field_name, field_value)

        elif isinstance(field_value, Callable):
            value = field_value()
        else:
            self._validate_scalar_field_value(resource, field_name, field_value)
            value = field_value

        setattr(resource, field_name, value)

    def _check_required_fields(self):
        required_fields = self.required_fields()
        if required_fields:
            if not self.field_values:
                raise ValueError(f"Missing required fields: {','.join(required_fields)}")
            if not set(required_fields).issubset(set(self.field_values.keys())):
                missing_fields = set(required_fields) - set(self.field_values.keys())
                raise ValueError(f"Missing required fields: {','.join(missing_fields)}")

    def _generate_resource_value_from_dict(self, resource: Resource, field_name: str, field_value: dict):
        pass

    def _generate_resource_value_from_list(self, resource: Resource, field_name: str, field_value: list):
        pass

    def _validate_scalar_field_value(self, resource: Resource, field_name: str, field_value: Union[str, int, float]):
        pass
