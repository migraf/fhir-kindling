import random
from typing import List, Optional, Type, Union
from uuid import uuid4

import matplotlib.pyplot as plt
import networkx as nx
from fhir.resources import FHIRAbstractModel, get_fhir_model_class
from fhir.resources.fhirresourcemodel import FHIRResourceModel
from fhir.resources.fhirtypes import ReferenceType
from fhir.resources.patient import Patient
from fhir.resources.reference import Reference
from pydantic import BaseModel, Field

from fhir_kindling import FhirServer
from fhir_kindling.generators.base import BaseGenerator
from fhir_kindling.generators.patient import PatientGenerator
from fhir_kindling.generators.resource_generator import ResourceGenerator
from fhir_kindling.util import get_resource_fields


class DataSetResourceGenerator(BaseModel):
    name: str
    generator: BaseGenerator
    depends_on: Optional[Union[str, List[str]]] = None
    reference_field: Optional[Union[str, List[str]]] = None
    likelihood: float

    class Config:
        arbitrary_types_allowed = True


class GeneratedResources(BaseModel):
    resource_type: str
    resources: List[dict] = Field(default_factory=list)
    reference_key: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


class DataSet(BaseModel):
    name: str
    patients: List[Patient]
    resources: Optional[List[GeneratedResources]]

    class Config:
        arbitrary_types_allowed = True

    def upload(self, server: FhirServer) -> tuple:
        # first upload the patients for referential integrity
        patient_ids = [patient.id for patient in self.patients]
        patient_response = server.add_all(self.patients)
        # replace the initially generated reference with the server generated ones

        # iterate over the server generated references along with the initially generated ids
        for reference, patient_id in zip(patient_response.references, patient_ids):
            # iterate over all the generated resource objects
            for generated_resources in self.resources:
                # and their resources
                for resource in generated_resources.resources:
                    # replace the reference parameter with the server generated one
                    resource_reference = resource.get(generated_resources.reference_key)
                    if patient_id in resource_reference["reference"]:
                        resource[generated_resources.reference_key] = {
                            "reference": reference.reference
                        }

        # upload the resources
        generated_resources = []
        for generated_resources_object in self.resources:
            generated_resources.extend(generated_resources_object.resources)
        resource_response = server.add_all(generated_resources)

        return patient_response, resource_response


class DatasetGenerator:
    """
    Generates a dataset of FHIR resources.
    """

    def __init__(self, base_resource: str = "Patient", n: int = None, name: str = None):
        self.name = name if name else str(uuid4())

        if base_resource == "Patient":
            self.base_resource = get_fhir_model_class(base_resource)
        else:
            raise NotImplementedError(
                "DatasetGenerator not implemented with {} as a base resource".format(
                    base_resource
                )
            )
        self.n = n
        self.generators: List[DataSetResourceGenerator] = []
        self._references = None
        self._patients = None
        self._dataset: DataSet = None
        self._nodes = set()
        self._graph = nx.DiGraph()
        self._resource_types = set()

        self.setup()

    def setup(self):
        # add base generator
        self.add_resource_generator(
            PatientGenerator(generate_ids=True, n=1),
            name="base",
            depends_on=None,
            reference_field=None,
            likelihood=1.0,
        )

    def add_resource_generator(
        self,
        resource_generator: ResourceGenerator,
        name: str,
        depends_on: Union[str, List[str]] = "base",
        reference_field: Union[str, List[str], None] = None,
        likelihood: float = 1.0,
    ) -> "DatasetGenerator":
        # make sure that the node names are unique
        if name in self._nodes:
            raise ValueError("A generator with the name {} already exists".format(name))
        else:
            self._nodes.add(name)

        self._resource_types.add(resource_generator.resource.get_resource_type())

        generator = DataSetResourceGenerator(
            name=name,
            generator=resource_generator,
            depends_on=depends_on,
            reference_field=reference_field,
            likelihood=likelihood,
        )

        # add the generator to the graph

        self.generators.append(generator)
        self._add_generator_to_graph(generator)

        return self

    def _add_generator_to_graph(self, generator: DataSetResourceGenerator):
        self._graph.add_node(generator.name, generator=generator)
        if generator.depends_on:
            if isinstance(generator.depends_on, str):
                self._graph.add_edge(
                    generator.depends_on,
                    generator.name,
                    likelihood=generator.likelihood,
                    reference_field=generator.reference_field,
                )
            else:
                for dependency in generator.depends_on:
                    self._graph.add_edge(dependency, generator.name)

    def generate(self, ids: bool = True) -> DataSet:
        """
        Generate a dataset of FHIR resources according to the given conditions

        Args:
            ids:

        Returns:

        """
        if self.generators:
            self._setup_dataset()
            self._patients, self._references = PatientGenerator(
                self.n, generate_ids=ids
            ).generate(references=True)
            for reference in self._references:
                for generator in self.generators:
                    # todo resolve interdependencies
                    if random.random() > generator.likelihood:
                        continue
                    # generate an id to use in put request with the server
                    resource = generator.generator.generate(
                        disable_validation=True, generate_ids=True
                    )
                    self._add_reference_param(resource, reference)

                    # construct the resource object
                    resource_type = generator.generator.resource.get_resource_type()
                    resource = get_fhir_model_class(resource_type)(**resource.dict())

                    # store the generated resource
                    self._store_generated_resource(
                        resource, resource_type=resource_type
                    )

            # add the patient resources
            self._dataset.patients = self._patients
            # validate data set
            return DataSet(**self._dataset.dict())

        else:
            patient_generator = PatientGenerator(
                n=self.n if self.n else 100, generate_ids=ids
            )
            patients = patient_generator.generate()
            return DataSet(name=self.name, patients=patients)

    def graph(self) -> nx.DiGraph:
        if not self._graph:
            self._graph = self._generate_resource_graph()
        return self._graph

    def _generate_resource_graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        for generator in self.generators:
            graph.add_node(generator.name)
            if generator.depends_on:
                if isinstance(generator.depends_on, str):
                    graph.add_edge(generator.depends_on, generator.name)
                else:
                    for dependency in generator.depends_on:
                        graph.add_edge(dependency, generator.name)
        return graph

    def explain(self):
        figure = self.draw_graph()
        figure.show()

    def draw_graph(self):
        graph = self.graph()
        pos = nx.spring_layout(graph)
        edge_labels = nx.get_edge_attributes(graph, "likelihood")
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
        nx.draw(graph, pos, with_labels=True)
        return plt

    def _add_reference_param(self, resource: FHIRResourceModel, reference: Reference):
        # check if a reference field is present for the given resource type if not detect first required reference
        reference_field = self._reference_fields.get(
            resource.get_resource_type(), self._get_required_reference(resource)
        )
        resource.__setattr__(reference_field, reference)

    @staticmethod
    def _get_required_reference(
        resource: Union[FHIRResourceModel, Type[FHIRAbstractModel]]
    ) -> str:
        fields = get_resource_fields(resource)
        required_fields = []
        for field in fields:
            if field.required:
                # todo check this further
                # add the reference to the required reference fields
                if field.type_ == ReferenceType:
                    required_fields.append(field.name)
            if field.name in ["patient", "subject"]:
                required_fields.append(field.name)
        # if there is only one reference field return it

        if len(required_fields) == 1:
            reference = required_fields[0]
        # iterate over the reference fields and return the best match patient -> subject
        else:
            reference = None
            for field in set(required_fields):
                if field == "patient":
                    reference = field
                    break
                elif field == "subject":
                    reference = field
                else:
                    raise ValueError(
                        f"No reference field found for {resource.get_resource_type()}"
                    )
        return reference

    def _store_generated_resource(
        self, resource: Union[FHIRResourceModel, FHIRAbstractModel], resource_type: str
    ):
        # todo improve this
        for store in self._dataset.resources:
            if store.resource_type == resource_type:
                store.resources.append(resource.dict(exclude_none=True))

    def _setup_dataset(self):
        dataset = DataSet.construct(resources=[])
        if self.name:
            dataset.name = self.name
        for resource in self._resource_types:
            # find the reference field
            reference_field = self._get_required_reference(
                get_fhir_model_class(resource)
            )
            self._reference_fields[resource] = reference_field
            # set up an initial empty resource store with
            dataset.resources.append(
                GeneratedResources(
                    resource_type=resource, reference_key=reference_field
                )
            )

        self._dataset = dataset

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(name={self.name}, resource_types={self._resource_types}, n={self.n},"
            f" generators={self.generators})>"
        )
