from datetime import datetime
from enum import Enum
from typing import List, Union

import pendulum
from fhir.resources.resource import Resource
from pendulum.datetime import DateTime

from fhir_kindling.generators.base import BaseGenerator
from fhir_kindling.generators.resource_generator import ResourceGenerator
from fhir_kindling.serde.json import json_dict
from fhir_kindling.util.resources import check_resource_contains_field


class Frequencies(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class TimeUnits(str, Enum):
    SECONDS = "s"
    MINUTES = "m"
    HOURS = "h"
    DAYS = "d"
    WEEKS = "w"
    MONTHS = "m"
    YEARS = "y"


class TimeSeriesGenerator(BaseGenerator):
    resource_generator: ResourceGenerator
    time_field: str
    start: DateTime
    end: Union[DateTime, None]
    freq: Union[Frequencies, str]
    n: Union[int, None]
    period: Union[int, None]
    period_unit: Union[TimeUnits, str, None]

    def __init__(
        self,
        resource_generator: ResourceGenerator,
        time_field: str,
        start: DateTime,
        end: Union[DateTime, None] = None,
        freq: Union[Frequencies, str] = Frequencies.DAILY,
        n: Union[int, None] = None,
        period: Union[int, None] = None,
        period_unit: Union[TimeUnits, str, None] = None,
    ) -> None:
        self.generator = resource_generator
        self.time_field = time_field
        self.n = n
        self._prev_time: Union[DateTime, None] = None
        self.generate_ids = True

        self._validate_args(freq, period, period_unit, start, end, n)

    def generate(
        self, generate_ids: bool = True, as_dict: bool = False
    ) -> Union[List[Resource], List[dict]]:
        self.generate_ids = generate_ids
        if self.n is None:
            return self._generate_by_end(as_dict=as_dict)
        else:
            return self._generate_by_n(as_dict=as_dict)

    def _generate_by_end(self, as_dict: bool) -> List[Resource]:
        resources = []
        current_time = self._get_next_time()
        while current_time < self.end:
            model = self._generate_resource(current_time, as_dict=as_dict)
            current_time = self._get_next_time()
            resources.append(model)

        return resources

    def _generate_by_n(self, as_dict: bool) -> List[Resource]:
        resources = []
        for _ in range(self.n):
            next_time = self._get_next_time()
            model = self._generate_resource(next_time, as_dict=as_dict)
            resources.append(model)
        return resources

    def _generate_resource(
        self, time: DateTime, as_dict: bool
    ) -> Union[Resource, dict]:
        resource = json_dict(self.generator.generate(generate_ids=self.generate_ids))
        resource[self.time_field] = time.isoformat()

        if as_dict:
            return resource

        model = self.generator.resource(**resource)
        return model

    def _get_next_time(self) -> datetime:
        """Get the next time in the series based on the frequency. Updates the internal state of the generator.

        Raises:
            ValueError: If the frequency is not valid

        Returns:
            _description
        """
        if not self._prev_time:
            self._prev_time = self.start
            return self.start

        next_time = None
        if self.freq == Frequencies.HOURLY:
            next_time = self._prev_time.add(hours=1)
        elif self.freq == Frequencies.DAILY:
            next_time = self._prev_time.add(days=1)
        elif self.freq == Frequencies.WEEKLY:
            next_time = self._prev_time.add(weeks=1)
        elif self.freq == Frequencies.MONTHLY:
            next_time = self._prev_time.add(months=1)
        elif self.freq == Frequencies.YEARLY:
            next_time = self._prev_time.add(years=1)
        else:
            raise ValueError(f"Invalid frequency: {self.freq}")
        #
        self._prev_time = next_time
        return next_time

    def _validate_args(self, freq, period, period_unit, start, end, n):
        if end is None and n is None:
            raise ValueError("Either end or n must be specified")
        if isinstance(freq, str):
            freq = Frequencies(freq)
        self.freq = freq
        # validate period input
        self._validate_period_input(period, period_unit)
        # validate time input
        self._validate_time_input(start, end)
        # check that the field is in the resource
        check_resource_contains_field(self.generator.resource, self.time_field)

    def _validate_period_input(self, period: int, period_unit: TimeUnits):
        if period is not None and period_unit is None:
            raise ValueError(
                "If period is specified, period_unit must also be specified"
            )
        if period is None and period_unit is not None:
            raise ValueError(
                "If period_unit is specified, period must also be specified"
            )
        if period is not None and period_unit is not None:
            if isinstance(period_unit, str):
                period_unit = TimeUnits(period_unit)
            self.period = period
            self.period_unit = period_unit

    def _validate_time_input(self, start: DateTime, end: DateTime):
        if isinstance(start, datetime):
            self.start = pendulum.instance(start)
        elif isinstance(start, DateTime):
            self.start = start
        else:
            raise ValueError(f"Invalid start datetime object: {type(start)}")

        if end:
            if isinstance(end, datetime):
                self.end = pendulum.instance(end)
            elif isinstance(end, DateTime):
                self.end = start
            else:
                raise ValueError(f"Invalid end datetime object: {type(end)}")
        else:
            self.end = None
