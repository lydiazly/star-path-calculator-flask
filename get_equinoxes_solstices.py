#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The main script to calculate and print coordinates in the console.
"""

import argparse
from datetime import datetime
import calendar
import sys
import os
from core import get_coords


# Ephemeris date range
EPH_DATE_MIN = [-3000, 1, 29]  # 29 January 3001 BCE
EPH_DATE_MAX = [3000, 5, 6]  # 6 May 3000 CE


def format_datetime(year: int, month: int, day: int,
                    hour: int = 12, minute: int = 0, second: int = 0):
    year_str = f"{year} CE" if year > 0 else f"{-year + 1} BCE"
    month_str = calendar.month_abbr[month]
    date_str = f"{day} {month_str} {year_str}"
    time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
    return [date_str, time_str]


EPH_DATE_MIN_STR, _ = format_datetime(*EPH_DATE_MIN)
EPH_DATE_MAX_STR, _ = format_datetime(*EPH_DATE_MAX)

prog = f"python {os.path.basename(__file__)}"
description = "Specify a date and time in UT1 to get the equinox and solstice coordinates in RA and DEC. The default time is 12:00:00."
epilog = f"""date range:
  {EPH_DATE_MIN_STR} \u2013 {EPH_DATE_MAX_STR} (UT1)
examples:
  # The current coordinates:
  {prog}\n
  # The coordinates on 1 Jan 3001 BCE, at 12:00:00:
  {prog} -3000\n
  # The coordinates on 5 April 3000 CE, at 18:00:00:
  {prog} 3000 Apr 5 -t 18
"""


def check_datetime_ranges(year: int, month: int, day: int,
                          hour: int, minute: int, second: int):
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


def main():
    parser = argparse.ArgumentParser(prog=prog, description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("year", type=int, nargs="?",
                        help="int, 0 is 1 BCE (default: this year)")
    parser.add_argument("month", type=str, nargs="?",
        help="e.g., January|Jan|1 (default: this month, or January if the year is provided)",)
    parser.add_argument("day", type=int, nargs="?",
        help="int, (default: today, or 1 if the year is provided)",)
    parser.add_argument("-t", dest="time", metavar="time", type=str, nargs="?",
        help="hh|hh:mm|hh:mm:ss, 24-hour format (default: 12:00:00)")
    args = parser.parse_args()

    now = datetime.now()

    # Set date
    if not args.year and args.year != 0:
        year, month, day = list(now.timetuple())[0:3]
    else:
        year  = args.year
        month = 1 if not args.month and args.month != 0 else args.month.capitalize()
        day   = 1 if not args.day and args.day     != 0 else args.day

    if str(month).isdigit():
        month = int(month)
    else:
        # Convert month name to int
        month_names = [*calendar.month_name, *calendar.month_abbr,]  # ['', 'January', ..., '', 'Jan', ...]
        try:
            month = month_names.index(month) % 13
        except ValueError:
            print(f"Invalid month name: '{args.month}'", file=sys.stderr)
            sys.exit(1)

    # Set time
    try:
        hour, minute, second, *_ = ([12, 0, 0] if not args.time else [*map(int, args.time.split(":")), 0, 0])
    except ValueError:
        print(f"Invalid time format (hh:mm or hh:mm:ss): '{args.time}'", file=sys.stderr)
        sys.exit(1)

    # Get coordinates
    datetime_list = [year, month, day, hour, minute, second]  # List(int)
    try:
        check_datetime_ranges(*datetime_list)
        results = get_coords(*datetime_list)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    date_str, time_str = format_datetime(*datetime_list)

    print(f"ICRS coordinates (J2000) of equinoxes and solstices on {date_str}, at {time_str}:")
    print("Vernal Equinox:")
    print(f'  ra = {results["vernal_ra"]}, dec = {results["vernal_dec"]}')
    print("Autumnal Equinox:")
    print(f'  ra = {results["autumnal_ra"]}, dec = {results["autumnal_dec"]}')
    print("Summer solstice:")
    print(f'  ra = {results["summer_ra"]}, dec = {results["summer_dec"]}')
    print("Winter solstice:")
    print(f'  ra = {results["winter_ra"]}, dec = {results["winter_dec"]}')


if __name__ == "__main__":
    main()
