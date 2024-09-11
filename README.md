# Star Path Calculator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![python](https://img.shields.io/badge/Python-3.10,_3.11-3776AB?logo=python&logoColor=white)](https://www.python.org) [![numpy](https://img.shields.io/badge/Numpy-2.0.1-013243?logo=numpy&logoColor=white)](https://numpy.org) [![pandas](https://img.shields.io/badge/Pandas-2.2.2-150458?logo=Pandas&logoColor=white)](https://pandas.pydata.org) [![matplotlib](https://img.shields.io/badge/Matplotlib-3.9.1.post1-12557C)](https://matplotlib.org) [![skyfield](https://img.shields.io/badge/Skyfield-1.49-BD9354)](https://rhodesmill.org/skyfield) [![juliandate](https://img.shields.io/badge/Juliandate-1.0.4-BD9354)](https://pypi.org/project/juliandate) [![tzfpy](https://img.shields.io/badge/tzfpy-0.15.5-blue)](https://github.com/ringsaturn/tzfpy) [![great-circle-calculator](https://img.shields.io/badge/Great_Circle_Calculator-1.3.1-brightgreen)](https://github.com/seangrogan/great_circle_calculator)

This repository contains the source code of our [Star Path Viewer](https://star-path-viewer.pages.dev/) website, along with Python scripts for executing the code.

[→ Team: Stardial](https://github.com/stardial-astro)

[→ Flask server](https://github.com/lydiazly/star-path-calculator-flask)

[→ React client](https://github.com/stardial-astro/star-path-viewer)

[→ Hosted data (star names)](https://github.com/stardial-astro/star-path-data)

## Table of Contents<!-- omit in toc -->

- [Star Path Calculator](#star-path-calculator)
  - [Overview](#overview)
  - [Features](#features)
  - [Installation](#installation)
  - [Script Usage](#script-usage)
    - [Get times and coordinates of the equinoxes and solstices in a given year](#get-times-and-coordinates-of-the-equinoxes-and-solstices-in-a-given-year)
    - [Plot a star's path on a given date at a given location](#plot-a-stars-path-on-a-given-date-at-a-given-location)
  - [Resources](#resources)
  - [References](#references)

## Overview

We are aiming to develop a user-friendly app to facilitate the research in history of astronomy, providing a convenient approach to help researchers get important astronomical information from thousands of years ago to far into the future.

## Features

- :globe_with_meridians: Obtain dates, times, and RA/Dec coordinates of equinoxes and solstices by specifying a year and location.
- :dizzy: Plots the star path and calculates the rising/setting times based on the provided date, location, and star information.
- :calendar: Covers a wide time span, from **3001 BCE to 3000 CE**.
- :ringed_planet: Uses the [JPL DE406 ephemeris and Hipparchus Catelogue](#resources) to calculate the planet and star positions for any given time.
- :telescope: Accounts for the [proper motion](https://en.wikipedia.org/wiki/Proper_motion) of a star if the Hipparcos Catalogue number is provided.
- :calendar: Accepts both **Gregorian** and **Julian** calendar date inputs.
- :star: Supports star or planet input by name, Hipparcos Catalogue number, or ICRS coordinates (RA, Dec).
- :night_with_stars: Displays star paths with distinct line styles for daytime, twilight, and nighttime.
- :clock1: Offers both [local time](#resources) and [UT1](https://en.wikipedia.org/wiki/Universal_Time) time in output details (*Daylight Saving Time is not included*).

## Installation

```sh
python3 -m pip install pandas matplotlib skyfield juliandate tzfpy
```

## Script Usage

### Get times and coordinates of the equinoxes and solstices in a given year

[get_equinoxes_solstices.py](./scripts/get_equinoxes_solstices.py)

Example:

```bash
python3 ./scripts/get_equinoxes_solstices.py -2000
```

<details>
<summary>Output:</summary>

```text
Dates, times, and ICRS coordinates (J2000) of the equinoxes and solstices in 2001 BCE:

[Vernal Equinox]   -2000-03-21 04:40:19.602 (UT1)
                   ra = 52.962, dec = 19.517

[Summer Solstice]  -2000-06-23 11:32:34.141 (UT1)
                   ra = 147.791, dec = 13.371

[Autumnal Equinox] -2000-09-22 05:50:58.094 (UT1)
                   ra = 232.955, dec = -19.515

[Winter Solstice]  -2000-12-19 15:18:26.852 (UT1)
                   ra = 327.784, dec = -13.373
```

</details>

<details>
<summary>Usage:</summary>

```text
usage: python get_equinoxes_solstices.py [-h] [year]

Specify a year to obtain the dates, times, and coordinates in RA and Dec of the equinoxes and solstices in that year.

positional arguments:
  year        int, 0 is 1 BCE (default: this year)

options:
  -h, --help  show this help message and exit

year range:
  -3000-01-29 – 3000-05-06 (Gregorian)
examples:
  # The current year:
  python get_equinoxes_solstices.py

  # The equinoxes and solstices of 2001 BCE:
  python get_equinoxes_solstices.py -2000
```

</details>

### Plot a star's path on a given date at a given location

[get_star_path.py](./scripts/get_star_path.py)

Example:

```bash
python3  .\get_star_path.py -2000 3 1 --lng 120 --lat 40 -o "jupiter"
```

<details>
<summary>Output:</summary>

```text
[Date (Gregorian)] 1 Mar 2001 BCE
[Location]         lat/lng = 40.000/120.000
[Celestial Object] Jupiter

[Point Details]
D1:
  alt = 17.721
  az  = 146.433
  time_local (Gregorian) = -2000-03-01T05:38:06+08:00
  time_ut1   (Gregorian) = -2000-02-29T21:38:06
  time_local (Julian)    = -2000-03-18T05:38:06+08:00
  time_ut1   (Julian)    = -2000-03-17T21:38:06
D2:
  alt = 20.742
  az  = 153.301
  time_local (Gregorian) = -2000-03-01T06:09:26+08:00
  time_ut1   (Gregorian) = -2000-02-29T22:09:26
  time_local (Julian)    = -2000-03-18T06:09:26+08:00
  time_ut1   (Julian)    = -2000-03-17T22:09:26
D3:
  alt = 22.828
  az  = 159.592
  time_local (Gregorian) = -2000-03-01T06:36:36+08:00
  time_ut1   (Gregorian) = -2000-02-29T22:36:36
  time_local (Julian)    = -2000-03-18T06:36:36+08:00
  time_ut1   (Julian)    = -2000-03-17T22:36:36
R:
  alt = -0.567
  az  = 122.008
  time_local (Gregorian) = -2000-03-01T03:25:27+08:00
  time_ut1   (Gregorian) = -2000-02-29T19:25:27
  time_local (Julian)    = -2000-03-18T03:25:27+08:00
  time_ut1   (Julian)    = -2000-03-17T19:25:27
T:
  alt = 25.648
  az  = 180.000
  time_local (Gregorian) = -2000-03-01T07:59:03+08:00
  time_ut1   (Gregorian) = -2000-02-29T23:59:03
  time_local (Julian)    = -2000-03-18T07:59:03+08:00
  time_ut1   (Julian)    = -2000-03-17T23:59:03
S:
  alt = -0.567
  az  = 237.995
  time_local (Gregorian) = -2000-03-01T12:32:40+08:00
  time_ut1   (Gregorian) = -2000-03-01T04:32:40
  time_local (Julian)    = -2000-03-18T12:32:40+08:00
  time_ut1   (Julian)    = -2000-03-18T04:32:40

SVG has been saved to 'sp_1726098588.844.svg'

```

</details>

The figure will be saved to `sp_{unix_timestamp}.svg`.

Note that Skyfield counts "34 arcminutes of atmospheric refraction at the horizon" [[link](https://rhodesmill.org/skyfield/almanac.html#risings-and-settings)].

<details>
<summary>Usage:</summary>

```text
usage: python get_star_path.py [-h] [--lat float] [--lng float] [-o str] [-j] [--name] [year] [month] [day]

Specify a local date, location, and celestial object to draw the star path. Daylight Saving Time is not included.

positional arguments:
  year                  int, 0 is 1 BCE (default: this year)
  month                 e.g., January|Jan|1 (default: this month, or January if the year is provided)
  day                   int (default: today, or 1 if the year is provided)

options:
  -h, --help            show this help message and exit
  --lat float           latitude in decimal degrees (default: 39.9042)
  --lng float, --lon float
                        longitude in decimal degrees (default: 116.4074)
  -o str, --obj str     planet name, Hipparchus Catalogue number, or the ICRS coordinates in the format 'ra,dec' (default: Mars)
  -j, --julian          use Julian calendar (default: Gregorian calendar)
  --name                print the proper name or the Bayer designation, if available (default: False)

date range:
  -3000-01-29 – 3000-05-06 (Gregorian)
examples:
  # Plot the star path of Mars:
  python get_star_path.py -o mars

  # Plot the star path of Vega by giving its Hipparcos Catalogue number:
  python get_star_path.py -o 91262

  # Plot the star path by giving the star's ICRS coordinates (RA, Dec):
  python get_star_path.py -o 310.7,-5.1
```

</details>

## Resources

- Ephemeris Data

  [JPL Planetary and Lunar Ephemerides](https://ssd.jpl.nasa.gov/planets/eph_export.html) (DE406)

- Hipparchus Catalogue

  [The Hipparcos and Tycho Catalogues](https://www.cosmos.esa.int/web/hipparcos/catalogues)
  [FTP](https://cdsarc.cds.unistra.fr/ftp/cats/I/239)

- Bayer Designation and Proper Name

  [FTP](https://cdsarc.cds.unistra.fr/ftp/I/239/version_cd/tables) (ident4, ident6)

- Timezone

  [Timezone Boundary Builder](https://github.com/evansiroky/timezone-boundary-builder)

## References

- [IMCCE, Paris Observatory](https://www.imcce.fr)

- [Rise, Set, and Twilight Definitions](https://aa.usno.navy.mil/faq/RST_defs)

- R. Tousey and M. J. Koomen, "The Visibility of Stars and Planets During Twilight," *Journal of the Optical Society of America*, Vol. 43, pp. 177-183, 1953. [Online]. Available: <https://opg.optica.org/josa/viewmedia.cfm?uri=josa-43-3-177&seq=0&html=true>
