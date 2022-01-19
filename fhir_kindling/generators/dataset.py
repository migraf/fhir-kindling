import random
from typing import List, Union, Optional
from uuid import uuid4

from fhir.resources import get_fhir_model_class
from fhir.resources.fhirresourcemodel import FHIRResourceModel
from fhir.resources.reference import Reference
from pydantic import BaseModel, Field
from fhir.resources.fhirtypes import ReferenceType

from fhir_kindling.generators.resource_generator import ResourceGenerator
from fhir_kindling.generators.field_generator import FieldGenerator
from fhir_kindling.generators.patient import PatientGenerator
from fhir_kindling.util import get_resource_fields


class GeneratedResources(BaseModel):
    resource_type: str
    resources: List[dict] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True


class DataSet(BaseModel):
    name: Optional[str] = Field(default_factory=uuid4)
    resources: Optional[List[GeneratedResources]]

    class Config:
        arbitrary_types_allowed = True


class DataSetResourceGenerator(BaseModel):
    name: str
    generator: ResourceGenerator
    depends_on: Optional[Union[str, List[str]]] = None
    likelihood: float

    class Config:
        arbitrary_types_allowed = True


class DatasetGenerator:
    """
    Generates a dataset for a FHIR resource.
    """

    def __init__(self, resource: str, n: int = None, name: str = None):

        self.name = name if name else str(uuid4())

        if resource == "Patient":
            self.resource = get_fhir_model_class(resource)
        else:
            raise NotImplementedError("DatasetGenerator for {} is not implemented".format(resource))
        self.n = n
        self.generators: List[DataSetResourceGenerator] = []
        self._references = None
        self._patients = None
        self._dataset: DataSet = None
        self._resource_types = set()

    def add_resource(self, resource_generator: ResourceGenerator, name: str = None,
                     depends_on: Union[str, List[str]] = None, likelihood: float = 1.0) -> 'DatasetGenerator':
        if not name:
            name = str(uuid4())
        self._resource_types.add(resource_generator.resource.get_resource_type())
        self.generators.append(
            DataSetResourceGenerator(
                name=name,
                generator=resource_generator,
                depends_on=depends_on,
                likelihood=likelihood
            )
        )
        return self

    def generate(self, ids: bool = True) -> DataSet:
        """
        Generate a dataset of FHIR resources according to the given conditions

        Args:
            ids:

        Returns:

        """
        if self.generators:
            self._setup_dataset()
            self._patients, self._references = PatientGenerator(self.n, generate_ids=ids).generate(references=True)
            for reference in self._references:
                for generator in self.generators:
                    # todo resolve interdependencies
                    if random.random() > generator.likelihood:
                        continue
                    resource = generator.generator.generate(disable_validation=True)
                    self._add_reference_param(resource, reference)

                    resource_type = generator.generator.resource.get_resource_type()
                    resource = get_fhir_model_class(resource_type)(**resource.dict())

                    # get storage for generated resources
                    self._store_generated_resource(resource, resource_type=resource_type)

            # add the patient resources
            self._dataset.resources = self._dataset.resources + self._patients
            return self._dataset

        else:
            patient_generator = PatientGenerator(n=self.n if self.n else 100, generate_ids=ids)
            patients = GeneratedResources(resource_type=self.resource.get_resource_type(),
                                          resources=[p.dict(exclude_none=True) for p in
                                                     patient_generator.generate(display=False)])

            return DataSet(name=self.name, resources=[patients])

    def _reference_field_generator(self, field: str, references) -> FieldGenerator:
        pass

    def explain(self):
        pass

    def _add_reference_param(self, resource: FHIRResourceModel, reference: Reference):
        fields = get_resource_fields(resource)

        for field in fields:
            if field.required:
                # todo check this further
                # add the reference to the required reference field
                if field.type_ == ReferenceType:
                    resource.__setattr__(field.name, reference)

    def _store_generated_resource(self, resource: FHIRResourceModel, resource_type: str):
        # todo improve this
        for store in self._dataset.resources:
            if store.resource_type == resource_type:
                store.resources.append(resource.dict(exclude_none=True))

    def _setup_dataset(self):

        dataset = DataSet(resources=[])
        if self.name:
            dataset.name = self.name
        for resource in self._resource_types:
            dataset.resources.append(GeneratedResources(resource_type=resource))

        self._dataset = dataset
