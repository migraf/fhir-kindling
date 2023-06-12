import json
import os

from dotenv import find_dotenv, load_dotenv

from fhir_kindling import FhirServer
from fhir_kindling.fhir_query.query_parameters import FhirQueryParameters


def main():
    load_dotenv(find_dotenv())
    url = "https://dev-fhir.grafm.de/blaze-1"

    user = os.getenv("PHT_SERVER_USER")
    password = os.getenv("PHT_SERVER_PASSWORD")

    params = {
        "resource": "Patient",
        "include_parameters": [
            {
                "resource": "Observation",
                "search_param": "subject",
                "reverse": True,
            },
            {
                "resource": "Condition",
                "search_param": "subject",
                "reverse": True,
            },
            {
                "resource": "DiagnosticReport",
                "search_param": "subject",
                "reverse": True,
            },
        ],
    }

    parameters = FhirQueryParameters(**params)

    server = FhirServer(api_address=url, username=user, password=password)
    # summary = server.summary(display=True)
    # print(summary)

    result = server.query(query_parameters=parameters).limit(200)

    with open("bundle.json", "w") as f:
        if isinstance(result.response, str):
            f.write(result.response)

        else:
            f.write(json.dumps(result.response, indent=4))

    print(result)


if __name__ == "__main__":
    main()
