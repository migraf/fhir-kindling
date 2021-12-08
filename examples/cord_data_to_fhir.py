import os
from dotenv import load_dotenv, find_dotenv
from fhir_kindling import FhirServer
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.condition import Condition
import pandas as pd

from fhir_kindling.generators import PatientGenerator


def split_cord_data():
    cord_test_data = pd.read_csv("../examples/cord/A2-1.csv")
    patients_per_station = int(len(cord_test_data) / 3)
    df_1 = cord_test_data[:patients_per_station]
    df_2 = cord_test_data[patients_per_station:2 * patients_per_station]
    df_3 = cord_test_data[2 * patients_per_station:]

    df_1.to_csv("../examples/cord/data_station_1.csv")
    df_2.to_csv("../examples/cord/data_station_2.csv")
    df_3.to_csv("../examples/cord/data_station_3.csv")


def upload_cord_data(csv_file, server_address):
    # Create the condition resources from the csv

    data = pd.read_csv(csv_file)
    code_system = "http://hl7.org/fhir/sid/icd-10"

    def make_condition_resource(row):
        condition = Condition.construct()

        condition.clinicalStatus = CodeableConcept(
            coding=[Coding(
                **{
                    "system": "http://hl7.org/fhir/condition-clinical",
                    "code": "active",
                    "display": "Active"
                }
            )]
        )

        condition.code = CodeableConcept(
            coding=[Coding(
                **{
                    "system": code_system,
                    "code": row["AngabeDiag1"],
                    "display": row["TextDiagnose1"],
                }
            ).dict()]
        )
        return condition

    data["condition_resource"] = data.apply(make_condition_resource, axis=1)

    condition_resource_list = list(data["condition_resource"])

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    provider_url = os.getenv("OIDC_PROVIDER_URL")

    n_patients = len(condition_resource_list)

    server = FhirServer(api_address=server_address, client_id=client_id, client_secret=client_secret,
                        oidc_provider_url=provider_url)

    patient_generator = PatientGenerator(n=n_patients)
    patients = patient_generator.generate()

    patients_create_response = server.add_all(patients)

    references = patients_create_response.references
    for j, condition in enumerate(condition_resource_list):
        # set the subject reference
        condition.subject = references[j]

    for cond in condition_resource_list:
        Condition.validate(cond)

    response = server.add_all(condition_resource_list)
    print(response)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    data_path = "../examples/cord/data_station_1.csv"
    # split_cord_data()
    server_1_address = "http://193.196.20.24:9001/fhir"
    server_2_address = "http://193.196.20.24:9002/fhir"
    server_3_address = "http://193.196.20.24:9003/fhir"

    local_server_address = "http://127.0.0.1:8080/fhir"

    upload_cord_data("../examples/cord/data_station_3.csv", local_server_address)
