#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The main script to plot the star path from the terminal.
"""

import argparse
from datetime import datetime
import calendar
import sys
import os
import base64

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.star_path import get_diagram
from utils.script_utils import format_datetime, format_datetime_iso, validate_datetime, format_timezone, EPH_DATE_MIN_STR, EPH_DATE_MAX_STR


prog = f"python {os.path.basename(__file__)}"
description = "Specify a local date, location, and celestial object to draw the star path. Daylight Saving Time is not included."
epilog = f"""date range:
  {EPH_DATE_MIN_STR} \u2013 {EPH_DATE_MAX_STR} (Gregorian)
examples:
  # Plot the star path of Mars:
  {prog} -o mars\n
  # Plot the star path of Vega by giving its Hipparcos Catalogue number:
  {prog} -o 91262\n
  # Plot the star path by giving the star's ICRS coordinates (RA, Dec):
  {prog} -o 310.7,-5.1
"""


def main():
    # TODO: edit help text
    parser = argparse.ArgumentParser(prog=prog, description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("year", type=int, nargs="?",
                        help="int, 0 is 1 BCE (default: this year)")
    parser.add_argument("month", type=str, nargs="?",
                        help="e.g., January|Jan|1 (default: this month, or January if the year is provided)")
    parser.add_argument("day", type=int, nargs="?",
                        help="int (default: today, or 1 if the year is provided)")
    parser.add_argument("--lat", metavar="float", type=float, default=39.9042,
                        help="latitude in decimal degrees (default: %(default)s)")
    parser.add_argument("--lng", "--lon", dest="lng", metavar="float", type=float, default=116.4074,
                        help="longitude in decimal degrees (default: %(default)s)")
    parser.add_argument("-o", "--obj", metavar="str", type=str, default="Mars",
                        help="planet name, Hipparchus Catalogue number, or the ICRS coordinates in the format 'ra,dec' (default: %(default)s)")
    parser.add_argument('-j', '--julian', action='store_true',
                        help='use Julian calendar (default: Gregorian calendar)')
    parser.add_argument('--name', action='store_true',
                        help='print the proper name or the Bayer designation, if available (default: False)')
    args = parser.parse_args()

    print_hip_name = args.name

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

    # Convert from local time to UT1 ------------------------------------------|
    if args.julian:
        from utils.time_utils import julian_to_gregorian
        year, month, day, *_ = julian_to_gregorian((year, month, day, 12))  # 12:00:00

    print(f"[Date (Gregorian)] {format_datetime(year, month, day)[0]}")

    # Set location ------------------------------------------------------------|
    lat = args.lat
    lng = args.lng
    print(f"[Location]         lat/lng = {lat:.3f}/{lng:.3f}")

    # Set the celestial object ------------------------------------------------|
    name, hip, radec = [None, -1, None]
    print("[Celestial Object]", end=" ")
    if ',' in args.obj:
        # (ra, dec)
        try:
            radec = tuple(map(float, args.obj.split(',')))
            print(f"RA/Dec: {radec[0]:.3f}/{radec[1]:.3f}")
        except ValueError:
            print(f"Invalid 'ra,dec' format: '{args.obj}'", file=sys.stderr)
            sys.exit(1)
    elif args.obj.isdigit():
        # Hipparchus Catalogue number
        hip = int(args.obj)
        if print_hip_name:
            from utils.star_utils import hip_to_name
            hip_name = hip_to_name(hip)
            if hip_name:
                print(f"Star Name: {hip_name},", end=" ")
        print(f"Hipparchus Catalogue Number: {hip}")
    else:
        # Planet name
        name = args.obj.lower()
        print(f"{name.capitalize()}")

    # Plot star path ---------------------------------------------------------|
    try:
        from utils.time_utils import find_timezone
        tz_id = find_timezone(lat=lat, lng=lng)
        # tz_id = "America/Vancouver"

        validate_datetime(year, month, day)
        results = get_diagram(year, month, day, lat=lat, lng=lng, tz_id=tz_id, name=name, hip=hip, radec=radec)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    # Write the SVG data to a file
    filename = f'sp_{results["diagram_id"]}.svg'

    # Decode the base64 data to get the SVG content
    svg_data = base64.b64decode(results["svg_data"]).decode('utf-8')
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(svg_data)

    print("\n[Point Details]")
    for item in results["annotations"]:
        if item['is_displayed']:
            print(f'{item["name"]}:')
            print(f'  alt = {item["alt"]:.3f}')
            print(f'  az  = {item["az"]:.3f}')
            print(f'  time_local (Gregorian) = {"T".join(format_datetime_iso(*item["time_local"]))}{format_timezone(item["time_zone"])}')
            print(f'  time_ut1   (Gregorian) = {"T".join(format_datetime_iso(*item["time_ut1"]))}')
            print(f'  time_local (Julian)    = {"T".join(format_datetime_iso(*item["time_local_julian"]))}{format_timezone(item["time_zone"])}')
            print(f'  time_ut1   (Julian)    = {"T".join(format_datetime_iso(*item["time_ut1_julian"]))}')
            # print(f'  time_zone = {item["time_zone"]}')

    print(f"\nSVG has been saved to '{filename}'")


if __name__ == "__main__":
    main()
