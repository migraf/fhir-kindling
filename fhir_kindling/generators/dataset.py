from typing import List

from fhir.resources import get_fhir_model_class
from fhir.resources.fhirresourcemodel import FHIRResourceModel
from pydantic import BaseModel

from fhir_kindling.generators.resource_generator import ResourceGenerator
from fhir_kindling.generators.field_generator import FieldGenerator
from fhir_kindling.generators.patient import PatientGenerator


class GeneratedResources(BaseModel):
    resource_type: str
    resources: List[dict]

    class Config:
        arbitrary_types_allowed = True


class DataSet(BaseModel):
    base_resource: str
    resources: List[GeneratedResources]

    class Config:
        arbitrary_types_allowed = True


class DatasetGenerator:
    """
    Generates a dataset for a FHIR resource.
    """

    def __init__(self, resource: str, n: int = None):

        if resource == "Patient":
            self.resource = get_fhir_model_class(resource)
        else:
            raise NotImplementedError("DatasetGenerator for {} is not implemented".format(resource))
        self.n = n
        self.conditions = None

    def has(self, generator: ResourceGenerator, name: str = None, depends_on: str = None) -> 'DatasetGenerator':
        pass

    def generate(self, ids: bool = False) -> DataSet:
        """
        Generate a dataset of FHIR resources according to the given conditions

        Args:
            ids:

        Returns:

        """
        if self.conditions:
            pass

        else:
            patient_generator = PatientGenerator(n=self.n if self.n else 100, generate_ids=ids)
            patients = GeneratedResources(resource_type=self.resource.get_resource_type(),
                                          resources=[p.dict() for p in patient_generator.generate(display=False)])

            return DataSet(base_resource=self.resource.get_resource_type(), resources=[patients])

    def explain(self):
        pass
