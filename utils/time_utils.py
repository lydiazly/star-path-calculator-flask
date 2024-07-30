# -*- coding: utf-8 -*-
# utils/time_utils.py
"""
Functions to handel time conversions.
"""

from typing import Tuple
from skyfield.api import load
from pytz import timezone
from datetime import datetime
from timezonefinder import TimezoneFinder

__all__ = ["get_standard_offset", "ut1_to_local_standard_time"]


def get_standard_offset(lng: float, lat: float) -> float:
    """
    Returns a location's standard offset from UTC in minutes.
    The daylight savings time is disregarded.
    """
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lng=lng, lat=lat)
    tz = timezone(timezone_name)

    now = datetime.now()
    return (tz.utcoffset(now) - tz.dst(now)).total_seconds() / 60


def ut1_to_local_standard_time(t: Tuple, lng: float, lat: float):
    '''
    add the offset to get the twilight times list in local standard time
    '''
    ts = load.timescale()
    offset_in_minutes = get_standard_offset(lng, lat)
    temp_t = (t[0], t[1], t[2], t[3], t[4]+offset_in_minutes, t[5])
    temp_t_local = ts.ut1(*temp_t)
    return temp_t_local.ut1_calendar()
