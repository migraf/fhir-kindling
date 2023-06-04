import abc

from fhir.resources.resource import Resource


class BaseGenerator(abc.ABC):
    resource: Resource

    @abc.abstractmethod
    def generate(self):
        pass
