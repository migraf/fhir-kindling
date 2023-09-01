import random
from typing import Dict, List, Optional, Type, Union
from uuid import uuid4

import matplotlib.pyplot as plt
import networkx as nx
from fhir.resources import (
    FHIRAbstractModel,
    construct_fhir_element,
    get_fhir_model_class,
)
from fhir.resources.fhirresourcemodel import FHIRResourceModel
from fhir.resources.fhirtypes import ReferenceType
from fhir.resources.reference import Reference
from pydantic import BaseModel
from tqdm.autonotebook import tqdm

from fhir_kindling.fhir_server import FhirServer
from fhir_kindling.fhir_server.ops.transfer import (
    reference_graph,
    resolve_reference_graph,
)
from fhir_kindling.generators.base import BaseGenerator
from fhir_kindling.generators.patient import PatientGenerator
from fhir_kindling.generators.resource_generator import ResourceGenerator
from fhir_kindling.generators.time_series_generator import TimeSeriesGenerator
from fhir_kindling.util import get_resource_fields


class DataSetResourceGenerator(BaseGenerator):
    name: str
    generator: BaseGenerator
    depends_on: Optional[Union[str, List[str]]] = None
    reference_field: Optional[
        Union[str, List[str], List[Union[str, None]], None]
    ] = None
    likelihood: float
    references: Dict[str, Reference]

    def __init__(
        self,
        name: str,
        generator: BaseGenerator,
        depends_on: Optional[Union[str, List[str]]] = None,
        reference_field: Optional[
            Union[str, List[str], List[Union[str, None]], None]
        ] = None,
        likelihood: float = 1.0,
    ):
        self.name = name
        self.generator = generator
        self.depends_on = depends_on
        self.reference_field = reference_field
        self.likelihood = likelihood
        self.references = {}

    def add_reference(self, reference_field: str, reference: Union[Reference, str]):
        if isinstance(reference, str):
            reference = {"reference": reference}
        elif isinstance(reference, Reference):
            reference = reference.dict()
        else:
            raise ValueError(
                f"Reference must be a string or a Reference object, got {type(reference)}"
            )

        self.references[reference_field] = reference

    def generate(self):
        # generate based on the likelihood
        if self.likelihood < 1.0:
            if random.random() > self.likelihood:
                return None

        if isinstance(self.generator, TimeSeriesGenerator):
            return self._generate_time_series()

        elif isinstance(self.generator, ResourceGenerator) or isinstance(
            self.generator, PatientGenerator
        ):
            return self._generate_single()

        else:
            raise ValueError(
                f"Expected ResourceGenerator or TimeSeriesGenerator, got {type(self.generator)}"
            )

    def _generate_single(self):
        base_resource_dict = self.generator.generate(generate_ids=True, as_dict=True)
        if self.references:
            # insert the references

            base_resource_dict = {**base_resource_dict, **self.references}

        resource = self.generator.resource(**base_resource_dict)
        return resource

    def _generate_time_series(self):
        resources = self.generator.generate(generate_ids=True, as_dict=True)
        if self.references:
            # insert the references
            for r in resources:
                for field, reference in self.references.items():
                    if isinstance(reference, str):
                        reference = {"reference": reference}
                    r[field] = reference
            # resources = [{**resource, **self.references} for resource in resources]
        if isinstance(self.generator, TimeSeriesGenerator):
            r_type = self.generator.generator.resource
            return [r_type(**resource) for resource in resources]
        else:
            raise ValueError(
                f"TimeSeriesGenerator expected, got {type(self.generator)}"
            )

    def __repr__(self) -> str:
        return f"<DataSetResourceGenerator {self.name}, generator={self.generator}>"


class DataSet(BaseModel):
    name: str
    base_resource: str
    resources: List
    resource_types: List[str]
    resource_counts: Dict[str, int]

    @property
    def n_resources(self):
        return len(self.resources)

    def size(self, human_readable: bool = False):
        """The size of the dataset in bytes"""

        size = sum(
            [
                len(resource.json(exclude_none=True, return_bytes=True))
                for resource in self.resources
            ]
        )
        if human_readable:
            return size / 1024 / 1024
        return size

    def upload(self, server: "FhirServer", display: bool = False):
        ds_graph = reference_graph(self.resources)
        result, _ = resolve_reference_graph(ds_graph, server, True, display=display)
        return result


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

    def generate(self, display: bool = False) -> DataSet:
        """
        Generate a dataset of FHIR resources according to the given conditions

        Args:
            ids:

        Returns:

        """
        resources = []
        for _ in tqdm(range(self.n), disable=not display, desc="Generating dataset"):
            batch = self._generate_resources_from_graph()
            added_resources = []

            for k, v in batch.items():
                if v is None:
                    continue

                if isinstance(v, list):
                    added_resources.extend(v)
                else:
                    added_resources.append(v)
            resources.extend(added_resources)

        dataset = self._make_data_set(resources)
        self._dataset = dataset
        return dataset

    def _make_data_set(self, resources: List[dict]) -> DataSet:
        # construct fhir elements
        fhir_resources = []

        resource_counts = dict()
        for resource in resources:
            if isinstance(resource, dict):
                resource = construct_fhir_element(resource["resourceType"], resource)
            else:
                fhir_resources.append(resource)

            type_count = resource_counts.get(resource.resource_type, 0)
            resource_counts[resource.resource_type] = type_count + 1

        dataset = DataSet(
            name=self.name,
            base_resource=self.base_resource.get_resource_type(),
            resources=fhir_resources,
            resource_types=list(self._resource_types),
            resource_counts=resource_counts,
        )

        return dataset

    def _generate_resources_from_graph(self):
        """
        Generate a set of resource based on the generator graph
        """

        results = {}

        graph = self.graph()
        # start with the base node/generator and work through the graph
        top_list = reversed(list(nx.topological_sort(graph)))
        for node in top_list:
            # get the edges from the node
            if not self._check_dependencies(node, results):
                continue
            # get the generator from the node data
            generator = self._get_node_generator(node)

            # get the dependencies and add them to the generator
            self._get_refs_for_generator(generator, results)

            result = generator.generate()
            results[node] = result
            # print("Generated", node, result[node])
        return results

    def _get_refs_for_generator(
        self, generator: DataSetResourceGenerator, result: dict
    ) -> dict:
        """Get the references resources for a generator from the results and insert a reference to them into
        the reference field of the generator

        Args:
            generator: the generator to get the references for
            result: dependencies that have already been generated

        Returns:
            None
        """
        if not generator.reference_field:
            return

        if isinstance(generator.reference_field, list):
            for dep, ref_field in zip(generator.depends_on, generator.reference_field):
                if not ref_field:
                    continue
                resource = result.get(dep)
                if resource is None:
                    raise ValueError(f"Resource {dep} is None")

                ref = self._get_ref_from_resource_dict(resource)
                generator.add_reference(reference=ref, reference_field=ref_field)
        else:
            resource = result.get(generator.depends_on)
            if resource is None:
                raise ValueError(f"Resource dependency {generator.depends_on} is None")
            ref = self._get_ref_from_resource_dict(resource)
            generator.add_reference(
                reference=ref, reference_field=generator.reference_field
            )

    def _get_ref_from_resource_dict(self, resource_dict: dict) -> str:
        """Get a reference dict from a resource dict by combining the resource type and id

        Args:
            resource_dict: dictionary representation of a fhir resource

        Returns:
            Dictionary representation of a fhir reference
        """

        if not isinstance(resource_dict, dict):
            resource_dict = resource_dict.dict()
        ref_string = "{}/{}".format(resource_dict["resourceType"], resource_dict["id"])

        return ref_string

    def _get_node_generator(self, node: str) -> DataSetResourceGenerator:
        """
        Get a generator by name

        Args:
            node: the name of the generator

        Returns:
            the generator
        """
        try:
            generator = self.graph().nodes[node]["generator"]
            return generator
        except KeyError:
            raise ValueError("No generator found for node {}".format(node))

    def _check_dependencies(self, node: str, result: dict) -> bool:
        """
        Check if a node has any dependencies

        Args:
            node: the node to check
        """

        graph = self.graph()
        edges = graph.edges(node, data=True)
        if not edges:
            return True

        dependencies_exists = True
        for edge in edges:
            _, dependency, data = edge
            if not result.get(dependency):
                dependencies_exists = False
                break

        return dependencies_exists

    def graph(self) -> nx.DiGraph:
        """
        Return a networkx graph of the descripting the resource generation process
        """
        if not self._graph:
            self._graph = self._generate_resource_graph()
        return self._graph

    def explain(self):
        figure = self.draw_graph()
        figure.show()

    def draw_graph(self):
        """
        Visualize the graph underlying the resource generation process
        """
        graph = self.graph()
        pos = nx.spring_layout(graph)
        edge_labels = nx.get_edge_attributes(graph, "likelihood")
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
        nx.draw(graph, pos, with_labels=True)
        return plt

    def add_resource_generator(
        self,
        resource_generator: BaseGenerator,
        name: str,
        depends_on: Union[str, List[str]] = "base",
        reference_field: Union[str, List[str], None] = None,
        likelihood: float = 1.0,
    ) -> "DatasetGenerator":
        """
        Adds a resource generator to the dataset generator.

        Args:
            resource_generator (ResourceGenerator): The resource generator to add.
            name (str): The name of the generator.
            depends_on (Union[str, List[str]], optional): The name(s) of the generator(s) that this generator
            depends on. Defaults to "base".
            reference_field (Union[str, List[str], None], optional): The name(s) of the reference field(s)
            that this generator uses to reference other resources. Defaults to None.
            likelihood (float, optional): The likelihood of generating this resource. Defaults to 1.0.

        Returns:
            DatasetGenerator: The dataset generator instance.

        Raises:
            ValueError: If a generator with the same name already exists.
        """

        # make sure that the node names are unique
        if name in self._nodes:
            raise ValueError("A generator with the name {} already exists".format(name))
        else:
            self._nodes.add(name)

        # validate the reference field
        self._validate_depends_and_reference(depends_on, reference_field)

        if isinstance(resource_generator, ResourceGenerator):
            self._resource_types.add(resource_generator.resource.get_resource_type())
        elif isinstance(resource_generator, TimeSeriesGenerator):
            self._resource_types.add(
                resource_generator.generator.resource.get_resource_type()
            )
        elif isinstance(resource_generator, PatientGenerator):
            self._resource_types.add("Patient")
        else:
            raise ValueError(
                "Resource generator must be of type ResourceGenerator or TimeSeriesGenerator"
                "got {}".format(type(resource_generator))
            )

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

    def _validate_depends_and_reference(
        self,
        depends_on: Union[str, List[str]],
        reference_field: Union[str, List[str], None],
    ):
        self._validate_depends(depends_on)

        if reference_field:
            if isinstance(depends_on, list) and isinstance(reference_field, list):
                if len(depends_on) != len(reference_field):
                    raise ValueError(
                        "When provided as list the number of reference fields must match the number of dependencies"
                    )
            elif isinstance(depends_on, list) and isinstance(reference_field, str):
                raise ValueError(
                    "When provided as list the number of reference fields must match the number of dependencies"
                )
            elif isinstance(depends_on, str) and isinstance(reference_field, str):
                pass
            else:
                raise ValueError(
                    "When provided as list the number of reference fields must match the number of dependencies"
                )

    def _validate_depends(
        self,
        depends_on: Union[str, List[str]],
    ):
        graph = self.graph()
        if depends_on:
            if isinstance(depends_on, list):
                for dependency in depends_on:
                    if dependency not in graph.nodes:
                        raise ValueError(
                            "The dependency {} does not exist in the graph".format(
                                dependency
                            )
                        )
            else:
                if depends_on not in graph.nodes:
                    raise ValueError(
                        "The dependency {} does not exist in the graph".format(
                            depends_on
                        )
                    )

    def _add_generator_to_graph(self, generator: DataSetResourceGenerator):
        self._graph.add_node(generator.name, generator=generator)
        if generator.depends_on:
            if isinstance(generator.depends_on, str):
                self._graph.add_edge(
                    generator.name,
                    generator.depends_on,
                    likelihood=generator.likelihood,
                    reference_field=generator.reference_field,
                )
            elif isinstance(generator.depends_on, list):
                for i, depends in enumerate(generator.depends_on):
                    self._graph.add_edge(
                        generator.name,
                        depends,
                        likelihood=generator.likelihood,
                        reference_field=generator.reference_field[i]
                        if generator.reference_field
                        else None,
                    )
            else:
                raise ValueError(
                    "depends_on must be either a string referencing a node or a list of strings "
                    "of node references. Got {}".format(type(generator.depends_on))
                )

    def _generate_resource_graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        for generator in self.generators:
            self._add_generator_to_graph(generator)
        return graph

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

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(name={self.name}, resource_types={self._resource_types}, n={self.n},"
            f" generators={self.generators})>"
        )
