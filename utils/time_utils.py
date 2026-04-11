# -*- coding: utf-8 -*-
# utils/time_utils.py
"""Functions to handle time conversions."""

# from typing import Tuple
from skyfield.api import load
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import juliandate

__all__ = [
    "get_tzid_by_tzfpy",
    "get_standard_offset_by_id",
    "ut1_to_standard_time",
    "ut1_to_local_mean_time",
    "julian_to_gregorian",
    "gregorian_to_julian",
]


tisca = load.timescale()
naive_dt = datetime(2000, 1, 1)


# def get_standard_offset(lng: float, lat: float) -> float:
#     """Returns a location's Standard Time offset in minutes.
#     The daylight savings time is disregarded.
#     """
#     tf = TimezoneFinder()
#     timezone_name = tf.timezone_at(lng=lng, lat=lat)
#     tz = timezone(timezone_name)
#     now = datetime.now()
#     return (tz.utcoffset(now) - tz.dst(now)).total_seconds() / 60


# def get_tzid_by_timezonefinder(lat: float, lng: float) -> str:
#     """Returns the time zone ID (https://github.com/MrMinimal64/timezonefinder)."""
#     from timezonefinder import TimezoneFinder
#     tf = TimezoneFinder()
#     tz_id = tf.timezone_at(lng=lng, lat=lat)
#     return tz_id


def get_tzid_by_tzfpy(lat: float, lng: float) -> str:
    """Returns the time zone ID (https://github.com/ringsaturn/tzfpy)."""
    from tzfpy import get_tz

    tz_id = get_tz(lng=lng, lat=lat)
    return tz_id


# def get_standard_offset_by_id(tz_id: str, dst: bool = False) -> float:
#     """Returns a location's Standard Time offset in minutes.
#     The daylight savings time is disregarded.
#     """
#     from pytz import timezone
#     tz = timezone(tz_id)
#     local_dt = tz.localize(naive_dt, is_dst=dst)
#     offset_in_minutes = local_dt.utcoffset().total_seconds() / 60
#     return offset_in_minutes


def get_standard_offset_by_id(tz_id: str) -> tuple[float, str]:
    """Retrieves the Standard Time offset for a specific time zone ID.
    - The offset is for **Standard Time**, ignoring Daylight Saving Time (DST).
    - The input `tz_id` is the IANA time zone ID of a location.
    - The year used to derive the offset is set as the **current year**.

    Returns:
        tuple: A tuple containing:
            offset_in_minutes (float): The Standard Time offset in minutes.
            tz_name (str): The current time zone name of this location.
                If the offset is non-standard, returns 'LMT'.

    Raises:
        ValueError: If `tz_id` is not a valid IANA timezone ID
    """
    current_year = datetime.now().year
    try:
        tz = ZoneInfo(tz_id)
        # Check both winter and summer dates and use noon to avoid midnight transition glitches
        # (most northern hemisphere standard times are active in January)
        dt_jan = datetime(current_year, 1, 1, 12, 0, tzinfo=tz)
        dt_jul = datetime(current_year, 7, 1, 12, 0, tzinfo=tz)

        # If DST is not in effect, dst() returns 0 - set it as the Standard Time
        if dt_jan.dst() == timedelta(0):
            std_dt = dt_jan
        elif dt_jul.dst() == timedelta(0):
            std_dt = dt_jul
        # If both in DST, fallback to take the one with the minimum offset
        else:
            std_dt = dt_jan if dt_jan.utcoffset() <= dt_jul.utcoffset() else dt_jul

        offset: timedelta | None = std_dt.utcoffset()
        # If non-standard, tzname() returns 'LMT'
        tz_name: str = std_dt.tzname() or ''
        offset_in_minutes: float = (
            (offset.total_seconds() / 60) if offset is not None else 0.0
        )
        return offset_in_minutes, tz_name

    except ZoneInfoNotFoundError:
        raise ValueError(f"'{tz_id}' is not a valid IANA time zone ID.")


def ut1_to_standard_time(t: tuple, offset_in_minutes: float) -> tuple:
    """Converts UT1 to Standard Time."""
    temp_t = (t[0], t[1], t[2], t[3], t[4] + offset_in_minutes, t[5])
    temp_t_standard = tisca.ut1(*temp_t).ut1_calendar()
    return temp_t_standard


def ut1_to_local_mean_time(t: tuple, lng: float) -> tuple:
    """Converts UT1 to Local Mean Time (LMT)."""
    offset_in_hours = lng / 15
    temp_t = (t[0], t[1], t[2], t[3] + offset_in_hours, t[4], t[5])
    temp_t_local_mean = tisca.ut1(*temp_t).ut1_calendar()
    return temp_t_local_mean


def julian_to_gregorian(t_julian: tuple) -> tuple:
    t_gregorian = juliandate.to_gregorian(juliandate.from_julian(*t_julian))
    t_gregorian = (
        *map(int, t_gregorian[0:5]),
        float(t_gregorian[-2] + t_gregorian[-1] / 1e6),
    )
    return t_gregorian


def gregorian_to_julian(t_gregorian: tuple) -> tuple:
    t_julian = juliandate.to_julian(juliandate.from_gregorian(*t_gregorian))
    t_julian = (*map(int, t_julian[0:5]), float(t_julian[-2] + t_julian[-1] / 1e6))
    return t_julian
