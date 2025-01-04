# -*- coding: utf-8 -*-
# utils/time_utils.py
"""
Functions to handle time conversions.
"""

# from typing import Tuple
from skyfield.api import load
from pytz import timezone
from datetime import datetime
import juliandate

__all__ = ["find_timezone", "get_standard_offset_by_id", "ut1_to_standard_time", "ut1_to_local_mean_time", "julian_to_gregorian", "gregorian_to_julian"]


tisca = load.timescale()
naive_dt = datetime(2000, 1, 1)


# def get_standard_offset(lng: float, lat: float) -> float:
#     """
#     Returns a location's standard offset from UTC in minutes.
#     The daylight savings time is disregarded.
#     """
#     tf = TimezoneFinder()
#     timezone_name = tf.timezone_at(lng=lng, lat=lat)
#     tz = timezone(timezone_name)

#     now = datetime.now()
#     return (tz.utcoffset(now) - tz.dst(now)).total_seconds() / 60


# def find_timezone(lat: float, lng: float) -> str:
#     from timezonefinder import TimezoneFinder
#     tf = TimezoneFinder()
#     tz_id = tf.timezone_at(lng=lng, lat=lat)
#     return tz_id


def find_timezone(lat: float, lng: float) -> str:
    """
    Returns the time zone identifier (https://github.com/ringsaturn/tzfpy).
    """
    from tzfpy import get_tz
    tz_id = get_tz(lng, lat)
    if tz_id == 'Asia/Urumqi':
        tz_id = 'Asia/Shanghai'
    return tz_id


def get_standard_offset_by_id(tz_id: str, dst: bool = False) -> float:
    """
    Returns a location's standard offset from UTC in minutes.
    The daylight savings time is disregarded.
    """
    tz = timezone(tz_id)
    local_dt = tz.localize(naive_dt, is_dst=dst)
    offset_in_minutes = local_dt.utcoffset().total_seconds() / 60
    return offset_in_minutes


def ut1_to_standard_time(t: tuple, offset_in_minutes: float) -> tuple:
    """
    Adds the offset to obtain twilight times in standard time.
    """
    temp_t = (t[0], t[1], t[2], t[3], t[4] + offset_in_minutes, t[5])
    temp_t_standard = tisca.ut1(*temp_t).ut1_calendar()
    return temp_t_standard


def ut1_to_local_mean_time(t: tuple, lng: float) -> tuple:
    """
    Adds the offset to obtain twilight times in local mean time.
    """
    offset_in_hours = lng / 15
    temp_t = (t[0], t[1], t[2], t[3] + offset_in_hours, t[4], t[5])
    temp_t_local_mean = tisca.ut1(*temp_t).ut1_calendar()
    return temp_t_local_mean


def julian_to_gregorian(t_julian: tuple) -> tuple:
    t_gregorian = juliandate.to_gregorian(juliandate.from_julian(*t_julian))
    t_gregorian = (*map(int, t_gregorian[0:5]), float(t_gregorian[-2] + t_gregorian[-1] / 1e6))
    return t_gregorian


def gregorian_to_julian(t_gregorian: tuple) -> tuple:
    t_julian = juliandate.to_julian(juliandate.from_gregorian(*t_gregorian))
    t_julian = (*map(int, t_julian[0:5]), float(t_julian[-2] + t_julian[-1] / 1e6))
    return t_julian
