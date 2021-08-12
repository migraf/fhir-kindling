import requests
import pendulum
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.condition import Condition
from pprint import pprint
from uuid import uuid4
from typing import Union, Tuple, List
import random


def generate_patients(n: int,
                      age_range: Union[Tuple[int, int], Tuple[pendulum.DateTime, pendulum.DateTime]] = None,
                      ) -> List[Patient]:

    patients = []
    for _ in range(n):
        patient_dict = _generate_patient(age_range=age_range)

    return patients


def _generate_patient(age_range: Union[Tuple[int, int], Tuple[pendulum.DateTime, pendulum.DateTime]] = None) -> dict:

    patient_dict = {
        "id": str(uuid4())
    }




