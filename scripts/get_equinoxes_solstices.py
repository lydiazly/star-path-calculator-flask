#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The main script to calculate and print coordinates from the terminal.
"""

import argparse
from datetime import datetime
import calendar
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.coordinates import get_coords
from utils.script_utils import format_datetime, check_datetime_ranges, EPH_DATE_MIN_STR, EPH_DATE_MAX_STR


prog = f"python {os.path.basename(__file__)}"
description = "Specify a date and time in UT1 to get the equinox and solstice coordinates in RA and Dec. The default time is 12:00:00."
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


def main():
    parser = argparse.ArgumentParser(prog=prog, description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("year", type=int, nargs="?",
                        help="int, 0 is 1 BCE (default: this year)")
    parser.add_argument("month", type=str, nargs="?",
                        help="e.g., January|Jan|1 (default: this month, or January if the year is provided)")
    parser.add_argument("day", type=int, nargs="?",
                        help="int (default: today, or 1 if the year is provided)")
    parser.add_argument("-t", dest="time", metavar="str", type=str, default="12:00:00",
                        help="hh|hh:mm|hh:mm:ss, 24-hour format (default: %(default)s)")
    args = parser.parse_args()

    # Set date ----------------------------------------------------------------|
    now = datetime.now()
    if args.year is None:
        year, month, day = list(now.timetuple())[0:3]
    else:
        year  = args.year
        month = 1 if args.month is None else args.month.capitalize()
        day   = 1 if args.day is None   else args.day

    if str(month).isdigit():
        month = int(month)
    else:
        # Convert month name to int
        month_names = [*calendar.month_name, *calendar.month_abbr]  # ['', 'January', ..., '', 'Jan', ...]
        try:
            month = month_names.index(month) % 13
        except ValueError:
            print(f"Invalid month name: '{args.month}'", file=sys.stderr)
            sys.exit(1)

    # Set time ----------------------------------------------------------------|
    try:
        hour, minute, second, *_ = [*args.time.split(":"), 0, 0]
        hour, minute, second = [int(hour), int(minute), float(second)]
    except ValueError:
        print(f"Invalid time format (hh:mm or hh:mm:ss): '{args.time}'", file=sys.stderr)
        sys.exit(1)

    # Get coordinates ---------------------------------------------------------|
    datetime_list = [year, month, day, hour, minute, second]  # [int, int, int, int, int, float]
    try:
        check_datetime_ranges(*datetime_list)
        results = get_coords(*datetime_list)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    date_str, time_str = format_datetime(*datetime_list)

    print(f"ICRS coordinates (J2000) of equinoxes and solstices on {date_str}, at {time_str}:")
    print("Vernal Equinox:")
    print(f'  {results["vernal_time"]}')
    print(f'  ra = {results["vernal_ra"]}, dec = {results["vernal_dec"]}')
    print("Summer Solstice:")
    print(f'  {results["summer_time"]}')
    print(f'  ra = {results["summer_ra"]}, dec = {results["summer_dec"]}')
    print("Autumnal Equinox:")
    print(f'  {results["autumnal_time"]}')
    print(f'  ra = {results["autumnal_ra"]}, dec = {results["autumnal_dec"]}')
    print("Winter Solstice:")
    print(f'  {results["winter_time"]}')
    print(f'  ra = {results["winter_ra"]}, dec = {results["winter_dec"]}')


if __name__ == "__main__":
    main()
