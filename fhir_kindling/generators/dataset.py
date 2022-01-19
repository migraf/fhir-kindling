from typing import List, Union, Optional
from uuid import uuid4

from fhir.resources import get_fhir_model_class
from fhir.resources.fhirresourcemodel import FHIRResourceModel
from pydantic import BaseModel, Field

from fhir_kindling.generators.resource_generator import ResourceGenerator
from fhir_kindling.generators.field_generator import FieldGenerator
from fhir_kindling.generators.patient import PatientGenerator


class GeneratedResources(BaseModel):
    resource_type: str
    resources: List[dict]

    class Config:
        arbitrary_types_allowed = True


class DataSet(BaseModel):
    name: Optional[str] = Field(default_factory=uuid4)
    resources: List[GeneratedResources]

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
        self.generators = []

    def add_resource(self, resource_generator: ResourceGenerator, name: str = None,
                     depends_on: Union[str, List[str]] = None, likelihood: float = 1.0) -> 'DatasetGenerator':
        if not name:
            name = str(uuid4())
        self.generators.append(
            DataSetResourceGenerator(
                name=name,
                generator=resource_generator,
                depends_on=depends_on,
                likelihood=likelihood
            )
        )
        return self

    def generate(self, ids: bool = False) -> DataSet:
        """
        Generate a dataset of FHIR resources according to the given conditions

        Args:
            ids:

        Returns:

        """
        if self.generators:

            pass

        else:
            patient_generator = PatientGenerator(n=self.n if self.n else 100, generate_ids=ids)
            patients = GeneratedResources(resource_type=self.resource.get_resource_type(),
                                          resources=[p.dict(exclude_none=True) for p in
                                                     patient_generator.generate(display=False)])

            return DataSet(name=self.name, resources=[patients])

    def explain(self):
        pass
