"""Top-level package for fhir-kindling."""

__author__ = """Michael Graf"""
__email__ = 'michael.graf@uni-tuebingen.de'
__version__ = '0.9.3'

from .fhir_server import FhirServer
from .fhir_query import FHIRQuerySync, FHIRQueryAsync
