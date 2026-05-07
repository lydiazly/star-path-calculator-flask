#!/usr/bin/env python
# -*- coding: utf-8 -*-
# scripts/get_star_path.py
"""Script to plot the star path."""

import argparse
import base64
import calendar
from datetime import datetime
import os
from pathlib import Path
import sys

from starpathcalculator.config import POINTS
from starpathcalculator.core.star_path import get_diagram
from starpathcalculator.utils.script_utils import (
    EPH_DATE_MIN_STR,
    EPH_DATE_MAX_STR,
    format_datetime,
    format_datetime_iso,
    validate_datetime,
    format_timezone,
)
from starpathcalculator.utils.time_utils import julian_to_gregorian, gregorian_to_julian, get_cc_date

# prog = f"python3 {os.path.basename(__file__)}"
prog = 'get-star-path'
description = "Specify a local date, location, and celestial object to draw the star path. Daylight Saving Time (DST) is ignored."
epilog = f"""date range:
  {EPH_DATE_MIN_STR}/{EPH_DATE_MAX_STR} (Gregorian)
examples:
  # Plot the star path of Mars:
  {prog} -o mars\n
  # Plot the star path of Vega by giving its Hipparcos Catalogue number:
  {prog} -o 91262\n
  # Plot the star path by giving the star's ICRS coordinates (RA, Dec):
  {prog} -o 310.7,-5.1
"""

# Read from env or in a subfolder 'data/' in the working directory
OUTPUT_DIR: Path = Path(os.getenv('OUTPUT_DIR', "./output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# print(f"[Output Location] {OUTPUT_DIR}")


def main():
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "year", type=int, nargs="?", help="int, 0 is 1 BCE (default: this year)"
    )
    parser.add_argument(
        "month",
        type=str,
        nargs="?",
        help="e.g., January|Jan|1 (default: this month, or January if the year is provided)",
    )
    parser.add_argument(
        "day",
        type=int,
        nargs="?",
        help="int (default: today, or 1 if the year is provided)",
    )
    parser.add_argument(
        "--lat",
        metavar="float",
        type=float,
        default=39.9042,
        help="latitude in decimal degrees (default: %(default)s)",
    )
    parser.add_argument(
        "--lng",
        "--lon",
        dest="lng",
        metavar="float",
        type=float,
        default=116.4074,
        help="longitude in decimal degrees (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--obj",
        metavar="str",
        type=str,
        default="Mars",
        help="planet name, Hipparcos Catalogue number, or the ICRS coordinates in the format 'ra,dec' (default: %(default)s)",
    )
    parser.add_argument(
        "-j",
        "--julian",
        action="store_true",
        help="use Julian calendar (default: Gregorian calendar)",
    )
    parser.add_argument(
        "--name",
        action="store_true",
        help="print the proper name or the Bayer designation, if available (default: False)",
    )
    parser.add_argument(
        "--no-svg",
        dest="svg",
        action="store_false",
        help="do not export the SVG image (default: export SVG)",
    )
    args = parser.parse_args()

    if sys.version_info < (3, 11):
        print("This program requires Python 3.11 or newer. Please upgrade your Python version.", file=sys.stderr)  # fmt: skip
        sys.exit(1)

    print_hip_name = args.name

    # Set date --------------------------------------------------------|
    now = datetime.now()
    if args.year is None:
        year, month, day = list(now.timetuple())[0:3]
    else:
        year = args.year
        month = 1 if args.month is None else args.month.capitalize()
        day = 1 if args.day is None else args.day

    if str(month).isdigit():
        month = int(month)
    else:
        # Convert month name to int
        # ['', 'January', ..., '', 'Jan', ...]
        month_names = [*calendar.month_name, *calendar.month_abbr]  # fmt: skip
        try:
            month = month_names.index(month) % 13
        except ValueError:
            print(f"Invalid month name: '{args.month}'", file=sys.stderr)
            sys.exit(1)

    # Convert from Julian to Gregorian --------------------------------|
    # 12:00:00
    if args.julian:
        year_j, month_j, day_j = year, month, day
        year, month, day, *_ = julian_to_gregorian((year_j, month_j, day_j, 12))
    else:
        year_j, month_j, day_j, *_ = gregorian_to_julian((year, month, day, 12))

    # Set location ----------------------------------------------------|
    lat = args.lat
    lng = args.lng

    # Set the celestial object ----------------------------------------|
    name, hip, radec = [None, -1, None]
    star_str = ''
    if ',' in args.obj:
        # (ra, dec)
        try:
            radec = tuple(map(float, args.obj.split(',')))
            star_str = f"RA/Dec: {radec[0]:.3f}/{radec[1]:.3f}"
        except ValueError:
            print(f"Invalid 'ra,dec' format: '{args.obj}'", file=sys.stderr)
            sys.exit(1)
    elif args.obj.isdigit():
        # Hipparcos Catalogue number
        hip = int(args.obj)
        if print_hip_name:
            from starpathcalculator.utils.star_utils import hip_to_name

            hip_name = hip_to_name(hip)
            if hip_name:
                star_str = f"Name: {hip_name}, "
        star_str += f"Hipparcos Catalogue Number: {hip}"
    else:
        # Planet name
        name = args.obj.lower()
        star_str = f"{name.capitalize()}"

    # Plot star path --------------------------------------------------|
    try:
        from starpathcalculator.utils.time_utils import get_tzid_by_tzfpy

        tz_id = get_tzid_by_tzfpy(lat=lat, lng=lng)
        # tz_id = "America/Vancouver"

        validate_datetime(year, month, day)
        results = get_diagram(year, month, day, lat=lat, lng=lng, tz_id=tz_id, name=name, hip=hip, radec=radec)  # fmt: skip
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    print(f"[Date (Gregorian)] {format_datetime(year, month, day)[0]}")
    print(f"[Date (Julian)]    {format_datetime(year_j, month_j, day_j)[0]}")
    # Convert to Chinese calendar if in UTC+8 -------------------------|
    if f"{results['offset'] / 60:.2f}" == '8.00':
        date_hans, date_hant = get_cc_date((year, month, day), (year_j, month_j, day_j))
        if date_hans is not None:
            print(f"[Date (Chinese)]   {date_hans['formatted']}")
    print(f"[Location]         lat/lng = {lat:.3f}/{lng:.3f}")
    print(f"[Celestial Object] {star_str}")

    def format_value(item: tuple[int, ...]) -> str:
        return delim.join(format_datetime_iso(*item))

    delim = 'T'
    tz_str = format_timezone(results["annotations"][0]["time_zone"])
    print()
    for item in results["annotations"]:
        if item['is_displayed']:
            title = f' [{item["name"]}] {POINTS[item["name"]]} '
            print(f'{title:-^56}')
            print(f'alt = {item["alt"]:.3f}')
            print(f'az  = {item["az"]:.3f}')
            print(f'time_local_mean (Gregorian) = {format_value(item["time_local_mean"])}')  # fmt: skip
            print(f'time_ut1        (Gregorian) = {format_value(item["time_ut1"])}')  # fmt: skip
            print(f'time_standard   (Gregorian) = {format_value(item["time_standard"])}{tz_str}')  # fmt: skip
            print(f'time_local_mean (Julian)    = {format_value(item["time_local_mean_julian"])}')  # fmt: skip
            print(f'time_ut1        (Julian)    = {format_value(item["time_ut1_julian"])}')  # fmt: skip
            print(f'time_standard   (Julian)    = {format_value(item["time_standard_julian"])}{tz_str}')  # fmt: skip

    # Write the SVG data to a file ------------------------------------|
    if args.svg:
        file_path = OUTPUT_DIR / f'sp_{results["diagram_id"]}.svg'
        # Decode the base64 data to get the SVG content
        svg_data = base64.b64decode(results["svg_data"]).decode('utf-8')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(svg_data)
        print(f"\nSVG has been saved to '{file_path}'")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    main()
