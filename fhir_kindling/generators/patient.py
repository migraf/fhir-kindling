import random
from typing import List, Tuple
from uuid import uuid4

import pandas as pd
from faker import Faker
from fhir.resources.humanname import HumanName
from fhir.resources.patient import Patient
from fhir.resources.reference import Reference

from fhir_kindling.generators.base import BaseGenerator
from fhir_kindling.serde.json import json_dict
from fhir_kindling.util.date_utils import (
    local_now,
    subtract,
)


class PatientGenerator(BaseGenerator):
    def __init__(
        self,
        n: int,
        age_range: Tuple[int, int] = None,
        gender_distribution: Tuple[float, float, float, float] = None,
        organisation: Reference = None,
        generate_ids: bool = False,
    ):
        self.resource = Patient
        self.n = n
        self.age_range = age_range
        self.gender_distribution = gender_distribution
        self._birthdate_range = None
        self.organisation = organisation
        self.generate_ids = generate_ids
        self.resources = None

    def generate(
        self,
        references: bool = False,
        generate_ids: bool = False,
        as_dict: bool = False,
    ):
        patients = self._generate()
        self.resources = patients

        if as_dict:
            resources = [json_dict(patient) for patient in patients]
            if self.n == 1:
                if references:
                    return resources[0], self._generate_references()[0]
                return resources[0]
            else:
                if references:
                    return resources, self._generate_references()
        else:
            if references and not self.generate_ids:
                raise ValueError("Cannot generate references without generating ids")
            elif references:
                return patients, self._generate_references()

        return patients

    def _generate(self):
        patients = []
        names = self._generate_patient_names(self.n)
        for name in names:
            patient = self._generate_patient_data(name=name)
            patients.append(patient)
        return patients

    def _generate_patient_data(self, name: Tuple[str, str]) -> Patient:
        first_name, last_name = name
        gender = random.choices(
            ["male", "female", "other", "unknown"],
            weights=self.gender_distribution
            if self.gender_distribution
            else [0.45, 0.45, 0.1, 0.0],
            k=1,
        )[0]

        name = HumanName(**{"family": last_name, "given": [first_name]})

        birthdate = self._generate_birthdate()
        patient_dict = {"gender": gender, "name": [name], "birthDate": birthdate}
        if self.organisation:
            patient_dict["managingOrganization"] = self.organisation

        patient_id = str(uuid4())
        patient_dict["id"] = patient_id

        return Patient(**patient_dict)

    @staticmethod
    def _generate_patient_names(n: int):
        fake = Faker()

        names = []
        for _ in range(n):
            split = fake.name().split(" ")
            family = split[-1]
            given = " ".join(split[:-1])
            names.append((given, family))
        return names

    def _generate_birthdate(self):
        if not self._birthdate_range:
            if self.age_range:
                if isinstance(self.age_range[0], int):
                    # generate age range from youngest to oldest based on the given tuple of ages
                    now = local_now()
                    youngest = pd.to_datetime(
                        (subtract(now, years=self.age_range[0])).isoformat()
                    )
                    oldest = pd.to_datetime(
                        (subtract(now, years=self.age_range[0])).isoformat()
                    )
                else:
                    raise ValueError(
                        f"Unsupported type ({type(self.age_range[0])}) for generating patient ages."
                        f"Only integers are supported."
                    )
            else:
                # generate age range from 18-101 years old
                now = local_now()
                youngest = pd.to_datetime(subtract(now, years=18).isoformat())
                oldest = pd.to_datetime(subtract(now, years=101).isoformat())

            # convert to utc time
            youngest = youngest.tz_localize(None)
            oldest = oldest.tz_localize(None)

            self._birthdate_range = (
                pd.date_range(oldest, youngest, freq="D").strftime("%Y-%m-%d").tolist()
            )

        birthdate = random.choice(self._birthdate_range)
        return birthdate

    def _generate_references(self) -> List[Reference]:
        return [
            Reference(reference=f"Patient/{patient.id}") for patient in self.resources
        ]

    def __repr__(self):
        return (
            f"<PatientGenerator(n={self.n}, age_range={self.age_range}, "
            f"gender_distribution={self.gender_distribution}>"
        )
