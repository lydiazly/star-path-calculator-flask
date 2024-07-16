# -*- coding: utf-8 -*-
# utils/script_utils.py
"""
Functions used only for scripts that are executed from the command line.
"""

import calendar
from config import EPH_DATE_MIN, EPH_DATE_MAX

__all__ = ["format_datetime", "check_datetime_ranges"]


def format_datetime(year: int, month: int, day: int,
                    hour: int = 12, minute: int = 0, second: float = 0):
    year_str = f"{year} CE" if year > 0 else f"{-year + 1} BCE"
    month_str = calendar.month_abbr[month]
    date_str = f"{day} {month_str} {year_str}"
    sec_str = f"{int(second):02d}" if float(second).is_integer() else f"{second:06.3f}"
    time_str = f"{hour:02d}:{minute:02d}:{sec_str}"
    return [date_str, time_str]


EPH_DATE_MIN_STR, _ = format_datetime(*EPH_DATE_MIN)
EPH_DATE_MAX_STR, _ = format_datetime(*EPH_DATE_MAX)


def check_datetime_ranges(year: int, month: int, day: int,
                          hour: int = 12, minute: int = 0, second: float = 0):
    day_max = 31
    if month == 2:
        day_max = 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
    elif month in [4, 6, 9, 11]:
        day_max = 30

    if not (1 <= month <= 12 and 1 <= day <= day_max):
        raise ValueError(f"Invalid date: [year, month, day] = [{year}, {month}, {day}]")

    if not (0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60):
        raise ValueError(f"Invalid time: {hour}:{minute}:{second}")

    if (
        year < EPH_DATE_MIN[0]
        or (year == EPH_DATE_MIN[0]
            and (month < EPH_DATE_MIN[1]
                or (month == EPH_DATE_MIN[1] and day < EPH_DATE_MIN[2])))
    ) or (
        year > EPH_DATE_MAX[0]
        or (year == EPH_DATE_MAX[0]
            and (month > EPH_DATE_MAX[1]
                or (month == EPH_DATE_MAX[1] and day > EPH_DATE_MAX[2])))
    ):
        raise ValueError(f"Out of the ephemeris date range: {EPH_DATE_MIN_STR} \u2013 {EPH_DATE_MAX_STR}")
