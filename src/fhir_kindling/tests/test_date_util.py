from datetime import datetime
from zoneinfo import ZoneInfo

from fhir_kindling.util.date_utils import (
    convert_to_local_datetime,
    parse_datetime,
    to_iso_string,
)


def test_parse_date():
    date_string = "2021-01-01T00:00:00+00:00"
    date = parse_datetime(date_string)

    assert date.year == 2021
    assert date.month == 1
    assert date.day == 1


def test_to_iso_string():
    date_string = "2021-01-01T00:00:00+00:00"
    date = parse_datetime(date_string)

    iso_string = to_iso_string(date)

    assert iso_string == date_string


def test_convert_to_local_datetime():
    utc_now = datetime.now(ZoneInfo("UTC"))

    local_date = convert_to_local_datetime(utc_now)

    zone_info = ZoneInfo("localtime")

    time_diff = zone_info.utcoffset(utc_now)

    utc_now = utc_now + time_diff

    assert local_date.year == utc_now.year
    assert local_date.month == utc_now.month
    assert local_date.day == utc_now.day
    assert local_date.hour == utc_now.hour
    assert local_date.minute == utc_now.minute
