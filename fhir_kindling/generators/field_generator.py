import random

from pydantic import BaseModel, validator, root_validator
from typing import List, Callable, Any, Optional


class FieldGenerator(BaseModel):
    field: str
    choices: Optional[List[Any]] = None
    choice_probabilities: Optional[List[float]] = None
    generator_function: Callable[[], Any] = None

    @validator("choice_probabilities", always=True)
    def check_probability_sum(cls, v):
        if v:
            if sum(v) != 1:
                raise ValueError("Probabilities must sum to 1")
            return v
        return None

    @root_validator
    def check_choices_and_probabilities(cls, values):
        if values.get("choices"):
            if values.get("choice_probabilities"):
                if len(values["choices"]) != len(values["choice_probabilities"]):
                    raise ValueError("Number of choices and probabilities must match")
            if values.get("generator_function"):
                raise ValueError("Cannot specify both choices and generator_function")

        elif not values.get("generator_function"):
            raise ValueError("Must specify either choices or generator_function")

        return values

    def generate(self):
        if self.choices:
            if self.choice_probabilities:
                return random.choices(self.choices, weights=self.choice_probabilities, k=1)[0]
            else:
                return random.choice(self.choices)
        else:
            return self.generator_function()
