import os

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.condition import Condition

from fhir_kindling import FhirServer
from fhir_kindling.generators import PatientGenerator


def split_cord_data():
    cord_test_data = pd.read_csv("cord/A2-1.csv")
    patients_per_station = int(len(cord_test_data) / 4)
    df_1 = cord_test_data[:patients_per_station]
    df_2 = cord_test_data[patients_per_station : 2 * patients_per_station]
    df_3 = cord_test_data[2 * patients_per_station : 3 * patients_per_station]
    df_4 = cord_test_data[3 * patients_per_station :]

    df_1.to_csv("../examples/cord/data_station_1.csv")
    df_2.to_csv("../examples/cord/data_station_2.csv")
    df_3.to_csv("../examples/cord/data_station_3.csv")
    df_4.to_csv("../examples/cord/data_station_4.csv")


def upload_cord_data(csv_file, server_address):
    # Create the condition resources from the csv

    data = pd.read_csv(csv_file)
    code_system = "http://hl7.org/fhir/sid/icd-10"

    def make_condition_resource(row):
        condition = Condition.construct()

        condition.clinicalStatus = CodeableConcept(
            coding=[
                Coding(
                    **{
                        "system": "http://hl7.org/fhir/condition-clinical",
                        "code": "active",
                        "display": "Active",
                    }
                )
            ]
        )

        condition.code = CodeableConcept(
            coding=[
                Coding(
                    **{
                        "system": code_system,
                        "code": row["AngabeDiag1"],
                        "display": row["TextDiagnose1"],
                    }
                ).dict()
            ]
        )
        return condition

    data["condition_resource"] = data.apply(make_condition_resource, axis=1)

    condition_resource_list = list(data["condition_resource"])

    n_patients = len(condition_resource_list)

    server = FhirServer(
        api_address=server_address,
        username=os.getenv("DEMO_USER"),
        password=os.getenv("DEMO_PW"),
    )

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


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    data_path = "../examples/cord/data_station_1.csv"
    # split_cord_data()
    server_1_address = "https://demo.personalhealthtrain.de/demo-fhir-1"
    server_2_address = "https://demo.personalhealthtrain.de/demo-fhir-2"
    server_3_address = "https://demo.personalhealthtrain.de/demo-fhir-3"
    server_4_address = "https://demo.personalhealthtrain.de/demo-fhir-4"

    local_server_address = "http://127.0.0.1:8080/fhir"

    upload_cord_data("cord/data_station_4.csv", server_4_address)
