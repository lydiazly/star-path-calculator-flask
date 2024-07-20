#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The main script to plot the star trail from the terminal.
"""

import argparse
from datetime import datetime
import calendar
import sys
import os
import base64

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.star_trail import get_diagram
from utils.script_utils import format_datetime, check_datetime_ranges, EPH_DATE_MIN_STR, EPH_DATE_MAX_STR


prog = f"python {os.path.basename(__file__)}"
description = "Specify a date to .... The input date is in UT1 by default."
epilog = f"""date range:
  {EPH_DATE_MIN_STR} \u2013 {EPH_DATE_MAX_STR} (UT1)
examples:
  # Plot the star trail of Mars:
  {prog} -o mars\n
  # Plot the star trail by giving the star's Hipparcos Catalog number:
  {prog} -o 87937\n
  # Plot the star trail by giving the star's ICRS coordinates:
  {prog} -o 10,10
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
                        help="latitude (default: %(default)s)")
    parser.add_argument("--lng", "--lon", dest="lng", metavar="float", type=float, default=116.4074,
                        help="longitude (default: %(default)s)")
    parser.add_argument("-o", "--obj", metavar="str", type=str, default="Mars",
                        help="planet name, Hipparchus catalogue number, or 'ra,dec' (default: %(default)s)")
    parser.add_argument('-l', '--local', action='store_true',
                        help='use local time (default: False)')
    parser.add_argument('-d', '--dir', metavar="path", type=str, default=".",
                        help='path to save output figures (default: %(default)s)')
    args = parser.parse_args()

    fig_dir = args.dir

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
    if args.local:
        # TODO: call the function to convert (remove `pass` after complete)
        pass
    
    print(f"[Date]             {format_datetime(year, month, day)[0]}")

    # Set location ------------------------------------------------------------|
    lat = args.lat
    lng = args.lng
    print(f"[Location]         (lat, lng) = ({lat}, {lng})")
    
    # Set the celestial object ------------------------------------------------|
    planet, hip, radec = [None, -1, None]
    print("[Celestial Object]", end=" ")
    if ',' in args.obj:
        # (ra, dec)
        try:
            radec = tuple(map(float, args.obj.split(',')))
            print(f"(ra, dec): ({radec[0]}, {radec[1]})")
        except ValueError:
            print(f"Invalid (ra, dec) format: '{args.obj}'", file=sys.stderr)
            sys.exit(1)
    elif args.obj.isdigit():
        # Hipparchus catalogue number
        hip = int(args.obj)
        print(f"Hipparchus: {hip}")
    else:
        # Planet name
        planet = args.obj.lower()
        print(f"{planet.capitalize()}")

    # Plot star trail ---------------------------------------------------------|
    try:
        check_datetime_ranges(year, month, day)
        results = get_diagram(year, month, day, lat=lat, lng=lng, planet=planet, hip=hip, radec=radec)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    
    # Write the SVG data to a file
    os.makedirs(fig_dir, exist_ok=True)
    filename = os.path.join(fig_dir, f'st_{results["diagram_id"]}.svg')

    # Decode the base64 data to get the SVG content
    svg_data = base64.b64decode(results["svg_data"]).decode('utf-8')
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(svg_data)
    
    print("\n[Annotations]")
    for item in results["annotations"]:
        if item['is_displayed']:
            _formatted_time_ut1   = ', '.join([f'{item["time_ut1"][0]:5d}']   + [f'{value:02d}' for value in item["time_ut1"][1:-1]]   + [f'{item["time_ut1"][-1]:06.3f}'])
            _formatted_time_local = ', '.join([f'{item["time_local"][0]:5d}'] + [f'{value:02d}' for value in item["time_local"][1:-1]] + [f'{item["time_local"][-1]:06.3f}'])
            _formatted_time_ut1_julian   = ', '.join([f'{item["time_ut1_julian"][0]:5d}']   + [f'{value:02d}' for value in item["time_ut1_julian"][1:-1]]   + [f'{item["time_ut1_julian"][-1]:06.3f}'])
            _formatted_time_local_julian = ', '.join([f'{item["time_local_julian"][0]:5d}'] + [f'{value:02d}' for value in item["time_local_julian"][1:-1]] + [f'{item["time_local_julian"][-1]:06.3f}'])
            print(f'{item["name"]}:')
            print(f'  alt = {item["alt"]}')
            print(f'  az  = {item["az"]}')
            print(f'  time_ut1            = ({_formatted_time_ut1})')
            print(f'  time_ut1 (Julian)   = ({_formatted_time_ut1_julian})')
            print(f'  time_local          = ({_formatted_time_local})')
            print(f'  time_local (Julian) = ({_formatted_time_local_julian})')
            print(f'  time_zone = {item["time_zone"]}')
    
    print(f"\nSVG has been saved to '{filename}'")


if __name__ == "__main__":
    main()
