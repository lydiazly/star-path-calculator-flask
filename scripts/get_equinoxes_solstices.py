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
from utils.script_utils import format_datetime, format_datetime_iso, validate_year, EPH_DATE_MIN_STR, EPH_DATE_MAX_STR


prog = f"python {os.path.basename(__file__)}"
# description = "Specify a date and time in UT1 to get the equinox and solstice coordinates in RA and Dec. The default time is 12:00:00."
# epilog = f"""date range:
#   {EPH_DATE_MIN_STR} \u2013 {EPH_DATE_MAX_STR} (UT1)
# examples:
#   # The current coordinates:
#   {prog}\n
#   # The coordinates on 1 Jan 3001 BCE, at 12:00:00:
#   {prog} -3000\n
#   # The coordinates on 5 April 3000 CE, at 18:00:00:
#   {prog} 3000 Apr 5 -t 18
# """
description = "Specify a year to obtain the dates, times, and coordinates in RA and Dec for the equinoxes and solstices of that year."
epilog = f"""year range:
  {EPH_DATE_MIN_STR} \u2013 {EPH_DATE_MAX_STR} (UT1)
examples:
  # The current year:
  {prog}\n
  # The equinoxes and solstices of 2001 BCE:
  {prog} -2000
"""


def main():
    parser = argparse.ArgumentParser(prog=prog, description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("year", type=int, nargs="?",
                        help="int, 0 is 1 BCE (default: this year)")
    # parser.add_argument("month", type=str, nargs="?",
    #                     help="e.g., January|Jan|1 (default: this month, or January if the year is provided)")
    # parser.add_argument("day", type=int, nargs="?",
    #                     help="int (default: today, or 1 if the year is provided)")
    # parser.add_argument("-t", dest="time", metavar="str", type=str, default="12:00:00",
    #                     help="hh|hh:mm|hh:mm:ss, 24-hour format (default: %(default)s)")
    args = parser.parse_args()

    # Set date ----------------------------------------------------------------|
    now = datetime.now()
    if args.year is None:
        year, month, day = list(now.timetuple())[0:3]
    else:
        year  = args.year
        # month = 1 if args.month is None else args.month.capitalize()
        # day   = 1 if args.day is None   else args.day

    # if str(month).isdigit():
    #     month = int(month)
    # else:
    #     # Convert month name to int
    #     month_names = [*calendar.month_name, *calendar.month_abbr]  # ['', 'January', ..., '', 'Jan', ...]
    #     try:
    #         month = month_names.index(month) % 13
    #     except ValueError:
    #         print(f"Invalid month name: '{args.month}'", file=sys.stderr)
    #         sys.exit(1)

    # Set time ----------------------------------------------------------------|
    # try:
    #     hour, minute, second, *_ = [*args.time.split(":"), 0, 0]
    #     hour, minute, second = [int(hour), int(minute), float(second)]
    # except ValueError:
    #     print(f"Invalid time format (hh:mm or hh:mm:ss): '{args.time}'", file=sys.stderr)
    #     sys.exit(1)

    # Get coordinates ---------------------------------------------------------|
    # datetime_list = [year, month, day, hour, minute, second]  # [int, int, int, int, int, float]
    datetime_list = [year,]  # [int, int, int, int, int, float]
    try:
        # validate_datetime(*datetime_list)
        validate_year(year)
        results = get_coords(*datetime_list)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    # date_str, time_str = format_datetime(*datetime_list)
    year_str = format_datetime(*datetime_list, year_only=True)

    # print(f"ICRS coordinates (J2000) of equinoxes and solstices on {date_str}, at {time_str}:")
    print(f"Dates, times, and ICRS coordinates (J2000) for the equinoxes and solstices of {year_str}:")
    print(f'\n[Vernal Equinox] {" ".join(format_datetime_iso(*results["vernal_time"]))} (UT1)')
    print(f'  ra = {results["vernal_ra"]:.3f}, dec = {results["vernal_dec"]:.3f}')
    print(f'\n[Summer Solstice] {" ".join(format_datetime_iso(*results["summer_time"]))} (UT1)')
    print(f'  ra = {results["summer_ra"]:.3f}, dec = {results["summer_dec"]:.3f}')
    print(f'\n[Autumnal Equinox] {" ".join(format_datetime_iso(*results["autumnal_time"]))} (UT1)')
    print(f'  ra = {results["autumnal_ra"]:.3f}, dec = {results["autumnal_dec"]:.3f}')
    print(f'\n[Winter Solstice] {" ".join(format_datetime_iso(*results["winter_time"]))} (UT1)')
    print(f'  ra = {results["winter_ra"]:.3f}, dec = {results["winter_dec"]:.3f}')


if __name__ == "__main__":
    main()
