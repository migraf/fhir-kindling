"""Top-level package for fhir-kindling."""

__author__ = """Michael Graf"""
__email__ = 'michael.graf@uni-tuebingen.de'
__version__ = '0.2.0'

from .upload import upload_bundle, upload_resource
from .delete import delete_resources
from .generate import generate_resources, generate_data_set
from .fhir_query import query_server, query_resource, query_with_string
