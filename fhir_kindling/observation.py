import random
from typing import List, Tuple

from fhir.resources.observation import Observation, ObservationComponent, ObservationReferenceRange
from resource_generator import FhirResourceGenerator
from fhir.resources.patient import Patient
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding


class ObservationGenerator(FhirResourceGenerator):
    def __init__(self,
                 n: int = None,
                 n_per_patient: int = None,
                 patients: List[Patient] = None,
                 coding_system: str = None,
                 codes: List[str] = None,
                 code_probabilities: List[float] = None,
                 units: List[str] = None,
                 value_ranges: List[Tuple[float, float]] = None
                 ):
        if n and n_per_patient:
            raise ValueError(
                "Both n and n_patients set. Observations can be generated either associated with patients or by "
                "themselves not both")

        if code_probabilities:
            if len(code_probabilities) != len(codes):
                raise ValueError("If probabilities are set they need to match the number of selected codes.\nNumber of"
                                 f"codes: {len(codes)} -- Number of probabilities: {len(code_probabilities)}")

        if n_per_patient and patients is None:
            raise ValueError("No patients given to generate resources for.")

        self.n = n
        self.n_per_patients = n_per_patient
        self.patients = patients
        self.coding_system = coding_system
        self.codes = codes
        self.code_probabilities = code_probabilities
        self.units = units
        self.value_ranges = value_ranges

    def generate(self, upload: bool = False, out_dir: str = None):

        if self.n:
            observations = self._generate_observations(self.n)
        elif self.patients:
            observations = self._generate_observations_for_patients()
        # super().generate(upload, out_dir)

        return observations

    def _generate_observations(self, n: int) -> List[Observation]:

        observations = []
        # todo add different status
        for i in range(n):
            observation = Observation(
                **{
                    "code": self._generate_code(),
                    "status": "final"
                }
            )
            observations.append(observation)
        print(observations)
        return observations

    def _generate_observations_for_patients(self):
        observations = []

        return observations

    def _generate_code(self) -> CodeableConcept:
        if self.code_probabilities:
            code = random.choices(self.codes, weights=self.code_probabilities)
        else:
            code = random.choice(self.codes)
        coding = Coding(
            **{
                "system": self.coding_system,
                "code": code
            }
        )

        code = CodeableConcept(
            **{
                "coding": [coding],
                "text": "loinc-code"
            }
        )

        return code


if __name__ == '__main__':
    code_system = "http://loinc.org"
    observation_codes = ["6598-7", "10839-9", "48425-3", "6597-9", "6598-7", "67151-1", "42757-5", "10839-9", "49563-0"]
    obs_generator = ObservationGenerator(n=100, coding_system=code_system, codes=observation_codes)
    obs_generator.generate()
