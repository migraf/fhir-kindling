import math
import os
from dotenv import load_dotenv, find_dotenv
from typing import Union, Tuple, List
import pendulum
import pandas as pd
import random
from tqdm import tqdm
from pathlib import Path
from pendulum import DateTime

from fhir.resources.reference import Reference
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName

from fhir_kindling.generators import FhirResourceGenerator
from fhir_kindling.fhir_server import FhirServer


class PatientGenerator(FhirResourceGenerator):
    def __init__(self,
                 n: int,
                 age_range: Union[Tuple[DateTime, DateTime], Tuple[int, int]] = None,
                 gender_distribution: Tuple[float, float, float, float] = None,
                 organisation: Reference = None,
                 generate_ids: bool = False):
        super().__init__(n, resource_type=Patient)
        self.age_range = age_range
        self.gender_distribution = gender_distribution
        self.birthdate_range = None
        self.organisation = organisation
        self.generate_ids = generate_ids

    def _generate(self, display: bool = False):
        patients = []
        names = self._generate_patient_names(self.n)
        for i in tqdm(range(self.n), desc=f"Generating {self.n} patients", disable=display):
            patient = self._generate_patient_data(name=names[i])
            patients.append(patient)
        return patients

    def _generate_patient_data(self, name: Tuple[str, str]) -> Patient:
        gender = random.choices(
            ["male", "female", "other", "unknown"],
            weights=self.gender_distribution if self.gender_distribution else [0.45, 0.45, 0.1, 0.0], k=1)[0]

        name = HumanName(**{"family": name[1], "given": [name[0]]})

        birthdate = self._generate_birthdate()
        patient_dict = {
            "gender": gender,
            "name": [name],
            "birthDate": birthdate
        }
        if self.organisation:
            patient_dict["managingOrganization"] = self.organisation

        return Patient(**patient_dict)

    @staticmethod
    def _generate_patient_names(n: int):

        p = Path(__file__).parent.joinpath("data").joinpath("first_names.txt")
        with open(p, "rb") as fnf:
            first_name_list = [fn.decode().strip().capitalize() for fn in fnf.readlines()]
        p = Path(__file__).parent.joinpath("data").joinpath("last_names.txt")
        with open(p, "rb") as lnf:
            last_name_list = [ln.decode().strip().capitalize() for ln in lnf.readlines()]

        first_names = random.choices(first_name_list, k=n)
        last_names = random.choices(last_name_list, k=n)
        names = list(zip(first_names, last_names))

        return names

    def _generate_birthdate(self):
        if not self.birthdate_range:
            if self.age_range:
                if isinstance(self.age_range[0], int):
                    # generate age range from 18-101 years old
                    now = pendulum.now()
                    youngest = pd.to_datetime((now - pendulum.duration(years=self.age_range[0])).to_date_string())
                    oldest = pd.to_datetime((now - pendulum.duration(years=self.age_range[1])).to_date_string())

                elif isinstance(self.age_range[0], DateTime):
                    youngest = self.age_range[0].to_date_string()
                    oldest = self.age_range[1].to_date_string()
                else:
                    raise ValueError(f"Unsupported type ({type(self.age_range[0])}) for generating patient ages."
                                     f"Only integers and datetime are supported.")
            else:
                # generate age range from 18-101 years old
                now = pendulum.now()
                youngest = pd.to_datetime((now - pendulum.duration(years=18)).to_date_string())
                oldest = pd.to_datetime((now - pendulum.duration(years=101)).to_date_string())

            self.birthdate_range = pd.date_range(oldest, youngest, freq="D").strftime('%Y-%m-%d').tolist()

        birthdate = random.choice(self.birthdate_range)
        return birthdate


class PatientResourceGenerator:

    def __init__(self, resource_generator: FhirResourceGenerator = None,
                 patients: Union[List[Patient], List[str], bool] = None,
                 n_per_patient: int = 1):
        self.patients = patients
        self.n_per_patients = n_per_patient
        self.resource_generator = resource_generator
        self.n = self.resource_generator.n
        self.resources = None

    def generate(self, patients=None, out_dir: str = None, filename: str = None, generate_ids: bool = False):
        if patients is None and self.patients is None:
            raise ValueError("No patients given to generate Resources for.")
        else:
            self.patients = patients
            # TODO use self patients and serialize newly generated patients to list
            self.resources = self.resource_generator.generate(generate_ids=generate_ids)
            self.update_with_patient_ids()
            if filename:
                if out_dir:
                    output_path = os.path.join(out_dir, filename)
                else:
                    output_path = filename
                with open(output_path, "w") as outputbundle:
                    bundle = self.resource_generator.make_bundle()
                    outputbundle.write(bundle.json(indent=2))

        return self.resources, self.resource_generator.make_bundle()

    def generate_patients(self, bundle=True):
        n_patients = math.ceil(float(self.n) / self.n_per_patients)
        patient_generator = PatientGenerator(n=n_patients)
        patients = patient_generator.generate()
        if bundle:
            return patient_generator.make_bundle()
        else:
            return patients

    def update_with_patient_ids(self):
        old_res = self.resources.copy()
        # Step with n per patient
        for index in range(0, len(self.resources), self.n_per_patients):
            patient_resources = self.resources[index: index + self.n_per_patients]
            for resource in patient_resources:
                resource.patient = {
                    "reference": self.patients[int(index / self.n_per_patients)],
                    "type": "Patient"
                }

        print(self.resources)


if __name__ == '__main__':
    # pprint(Patient.schema()["properties"])
    load_dotenv(find_dotenv())
    pg = PatientGenerator(n=100)
    pg.generate()
    bundle = pg.make_bundle()
    server = FhirServer(
        api_address="http://localhost:8080/fhir",
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL")
    )

    response = server.add_bundle(bundle)
    print(response.references)
