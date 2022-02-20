from fhir.resources.bundle import Bundle, BundleEntry


from fhir_kindling.fhir_query.query_response import QueryResponse


def parse_references(response: QueryResponse) -> dict:
    """
    Parses the references in a bundle.

    :param bundle: The bundle to parse.
    :return: A dictionary of references.
    """
    references = {}

    for resource in response.resources:
        pass