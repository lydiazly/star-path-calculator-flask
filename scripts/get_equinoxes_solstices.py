#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to calculate and print coordinates."""
import argparse
from datetime import datetime
import sys
import os

# Append the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.seasons import get_coords
from utils.script_utils import format_datetime, format_datetime_iso, validate_year, EPH_DATE_MIN, EPH_DATE_MAX


prog = f"python3 {os.path.basename(__file__)}"
description = "Specify a year to obtain the dates, times, and coordinates in RA and Dec of the equinoxes and solstices in that year."
epilog = f"""year range:
  {EPH_DATE_MIN[0]+1}/+{EPH_DATE_MAX[0]-1} (Gregorian)
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
    args = parser.parse_args()

    if sys.version_info < (3, 9):
        print("This program requires Python 3.9 or newer. Please upgrade your Python version.", file=sys.stderr)
        sys.exit(1)

    # Set date ----------------------------------------------------------------|
    now = datetime.now()
    if args.year is None:
        year, month, day = list(now.timetuple())[0:3]
    else:
        year  = args.year

    # Get Seasons -------------------------------------------------------------|
    datetime_list = [year,]
    try:
        # validate_datetime(*datetime_list)
        validate_year(year)
        results = get_coords(*datetime_list)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    year_str = format_datetime(*datetime_list, year_only=True)

    print(f"Dates, times, and ICRS coordinates (J2000) of the equinoxes and solstices in {year_str}:")
    print(f'\n[Vernal Equinox]   {" ".join(format_datetime_iso(*results["vernal_time"]))} (UT1)')
    print(f'                   ra = {results["vernal_ra"]:.3f}, dec = {results["vernal_dec"]:.3f}')
    print(f'\n[Summer Solstice]  {" ".join(format_datetime_iso(*results["summer_time"]))} (UT1)')
    print(f'                   ra = {results["summer_ra"]:.3f}, dec = {results["summer_dec"]:.3f}')
    print(f'\n[Autumnal Equinox] {" ".join(format_datetime_iso(*results["autumnal_time"]))} (UT1)')
    print(f'                   ra = {results["autumnal_ra"]:.3f}, dec = {results["autumnal_dec"]:.3f}')
    print(f'\n[Winter Solstice]  {" ".join(format_datetime_iso(*results["winter_time"]))} (UT1)')
    print(f'                   ra = {results["winter_ra"]:.3f}, dec = {results["winter_dec"]:.3f}')


if __name__ == "__main__":
    main()
