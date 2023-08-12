from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def local_now() -> datetime:
    """
    Get the current datetime in local time
    :return: datetime object
    """

    return datetime.now(ZoneInfo("localtime"))


def local_now_string() -> str:
    """
    Get the current datetime in local time as a string
    :return: string in ISO 8601 format
    """

    return local_now().isoformat()


def parse_datetime(date_string: str) -> datetime:
    """
    Parse a datetime string into a datetime object
    :param date_string: string to parse requires ISO 8601 date format
    :return: datetime object
    """

    return datetime.fromisoformat(date_string)


def to_iso_string(datetime: datetime) -> str:
    """
    Convert a datetime object to a string in ISO 8601 format
    :param date: datetime object
    :return: string in ISO 8601 format
    """

    return datetime.isoformat()


def convert_to_local_datetime(datetime: datetime) -> datetime:
    """
    Convert a datetime object to local time
    :param datetime: datetime object
    :return: datetime object in local time
    """

    local_timezone = ZoneInfo("localtime")
    return datetime.astimezone(local_timezone)


def add(
    datetime: datetime,
    years: int = 0,
    weeks: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> datetime:
    """Add days, hours, minutes, and seconds to a datetime object

    Args:
        datetime: the datetime object to add to
        days: days to add. Defaults to None.
        hours: Hours to add. Defaults to None.
        minutes: Minutes to add. Defaults to None.
        seconds: seconds to add. Defaults to None.

    Returns:
        the datetime object with the added time
    """

    if years != 0:
        weeks += years * 52

    dt_result = datetime + timedelta(
        weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds
    )
    return dt_result


def subtract(
    datetime: datetime,
    years: int = 0,
    weeks: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> datetime:
    """Subtract days, hours, minutes, and seconds from a datetime object"""

    if years != 0:
        weeks += years * 52
    dt_result = datetime - timedelta(
        weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds
    )
    return dt_result
