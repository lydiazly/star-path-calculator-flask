# -*- coding: utf-8 -*-
# utils/time_utils.py
"""
Functions to handle time conversions.
"""

from typing import Tuple, List
from skyfield.api import load
from pytz import timezone
from datetime import datetime
import juliandate

__all__ = ["find_timezone", "get_standard_offset_by_id", "ut1_to_local_standard_time", "ut1_to_local_standard_time_list", "julian_to_gregorian", "gregorian_to_julian"]


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

def find_timezone(lat: float, lng: float) -> str:
    from timezonefinder import TimezoneFinder
    tf = TimezoneFinder()
    tz_id = tf.timezone_at(lng=lng, lat=lat)
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


def ut1_to_local_standard_time(t: Tuple, offset_in_minutes: float) -> Tuple:
    '''
    Adds the offset to get the twilight times list in local standard time
    '''
    temp_t = (t[0], t[1], t[2], t[3], t[4] + offset_in_minutes, t[5])
    temp_t_local = tisca.ut1(*temp_t).ut1_calendar()
    return temp_t_local


def ut1_to_local_standard_time_list(t_list: List[Tuple], offset_in_minutes: float) -> List[Tuple]:
    '''
    Adds the offset to get the twilight times list in local standard time
    '''
    t_local = []
    for t in t_list:
        temp_t = (t[0], t[1], t[2], t[3], t[4] + offset_in_minutes, t[5])
        temp_t_local = tisca.ut1(*temp_t).ut1_calendar()
        t_local.append((*map(int, temp_t_local[0:5]), float(temp_t_local[-1])))
    return t_local


def julian_to_gregorian(t_julian: Tuple) -> Tuple:
    t_gregorian = juliandate.to_gregorian(juliandate.from_julian(*t_julian))
    t_gregorian = (*map(int, t_gregorian[0:5]), float(t_gregorian[-2] + t_gregorian[-1] / 1e6))
    return t_gregorian


def gregorian_to_julian(t_gregorian: Tuple) -> Tuple:
    t_julian = juliandate.to_julian(juliandate.from_gregorian(*t_gregorian))
    t_julian = (*map(int, t_julian[0:5]), float(t_julian[-2] + t_julian[-1] / 1e6))
    return t_julian
