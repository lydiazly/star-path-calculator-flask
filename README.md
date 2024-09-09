# Star Path Calculator

[![python](https://img.shields.io/badge/Python-3.10,_3.11-3776AB?logo=python&logoColor=white)](https://www.python.org) [![numpy](https://img.shields.io/badge/Numpy-2.0.1-013243?logo=numpy&logoColor=white)](https://numpy.org) [![pandas](https://img.shields.io/badge/Pandas-2.2.2-150458?logo=Pandas&logoColor=white)](https://pandas.pydata.org) [![matplotlib](https://img.shields.io/badge/Matplotlib-3.9.1.post1-12557C)](https://matplotlib.org) [![skyfield](https://img.shields.io/badge/Skyfield-1.49-BD9354)](https://rhodesmill.org/skyfield) [![juliandate](https://img.shields.io/badge/Juliandate-1.0.4-BD9354)](https://pypi.org/project/juliandate) [![tzfpy](https://img.shields.io/badge/tzfpy-0.15.5-blue)](https://github.com/ringsaturn/tzfpy) [![great-circle-calculator](https://img.shields.io/badge/Great_Circle_Calculator-1.3.1-brightgreen)](https://github.com/seangrogan/great_circle_calculator)

This repository contains the source code of our website [Star Path Viewer](https://stardial-astro.github.io/star-path-viewer).

[→ Team](https://github.com/stardial-astro)

[→ Flask server](https://github.com/lydiazly/star-path-calculator-flask)

[→ React client](https://github.com/stardial-astro/star-path-viewer)

## Table of Contents<!-- omit in toc -->

- [Overview](#overview)
- [Features](#features)
- [Install](#install)
- [Usage](#usage)
  - [Get Equinoxes and Solstices](#get-equinoxes-and-solstices)
  - [Plot a Star Path](#plot-a-star-path)
- [Resources](#resources)
- [References](#references)

## Overview

We are aiming to develop a user-friendly app to facilitate the research in history of astronomy, providing a convenient approach to help researchers get important astronomical information within a span of millennia from the past to the future.

## Features

- Obtain dates, times, and RA/Dec coordinates for equinoxes and solstices by specifying a year and location.
- Calculates and plots the star path and rising/setting times based on the provided date, location, and star information.
- Covers a wide time span, from 3001 BCE to 3000 CE.
- Uses the JPL DE406 ephemeris to calculate planetary positions for any given time.
- Accounts for proper motion if a Hipparcos Catalogue number is provided.
- Accepts both Gregorian and Julian calendar date inputs.
- Supports star or planet input by name, Hipparcos Catalogue number, or ICRS coordinates (RA, Dec).
- Displays star paths with distinct line styles for daytime, twilight, and nighttime.
- Offers both local time and UT1 time in output details (Daylight Saving Time is not included).

## Install

```sh
python3 -m pip install pandas matplotlib skyfield juliandate tzfpy
```

## Usage

### Get Equinoxes and Solstices

[get_equinoxes_solstices.py](./scripts/get_equinoxes_solstices.py)

Example:

```bash
python3 ./scripts/get_equinoxes_solstices.py -2000
```

<details>
<summary>Output:</summary>

```text
Dates, times, and ICRS coordinates (J2000) for the equinoxes and solstices of 2001 BCE:

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

Specify a year to obtain the dates, times, and coordinates in RA and Dec for the equinoxes and solstices of that year.

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

### Plot a Star Path

[get_star_path.py](./scripts/get_star_path.py)

Example:

```bash
python3 ./scripts/get_star_path.py -2000
```

<details>
<summary>Output:</summary>

```text
[Date (Gregorian)] 1 Jan 2001 BCE
[Location]         lat/lng = 39.904/116.407
[Celestial Object] Mars

[Point Details]
N1:
  alt = 49.530
  az  = 117.752
  time_local (Gregorian) = -2000-01-01T17:08:22+08:00
  time_ut1   (Gregorian) = -2000-01-01T09:08:22
  time_local (Julian)    = -2000-01-18T17:08:22+08:00
  time_ut1   (Julian)    = -2000-01-18T09:08:22
N2:
  alt = 54.497
  az  = 126.666
  time_local (Gregorian) = -2000-01-01T17:38:53+08:00
  time_ut1   (Gregorian) = -2000-01-01T09:38:53
  time_local (Julian)    = -2000-01-18T17:38:53+08:00
  time_ut1   (Julian)    = -2000-01-18T09:38:53
N3:
  alt = 59.305
  az  = 138.966
  time_local (Gregorian) = -2000-01-01T18:12:55+08:00
  time_ut1   (Gregorian) = -2000-01-01T10:12:55
  time_local (Julian)    = -2000-01-18T18:12:55+08:00
  time_ut1   (Julian)    = -2000-01-18T10:12:55
R:
  alt = -0.567
  az  = 70.008
  time_local (Gregorian) = -2000-01-01T12:40:27+08:00
  time_ut1   (Gregorian) = -2000-01-01T04:40:27
  time_local (Julian)    = -2000-01-18T12:40:27+08:00
  time_ut1   (Julian)    = -2000-01-18T04:40:27
T:
  alt = 64.948
  az  = 180.000
  time_local (Gregorian) = -2000-01-01T19:33:53+08:00
  time_ut1   (Gregorian) = -2000-01-01T11:33:53
  time_local (Julian)    = -2000-01-18T19:33:53+08:00
  time_ut1   (Julian)    = -2000-01-18T11:33:53
S:
  alt = -0.567
  az  = 290.056
  time_local (Gregorian) = -2000-01-02T02:27:30+08:00
  time_ut1   (Gregorian) = -2000-01-01T18:27:30
  time_local (Julian)    = -2000-01-19T02:27:30+08:00
  time_ut1   (Julian)    = -2000-01-18T18:27:30

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

  [JPL Planetary and Lunar Ephemerides](https://ssd.jpl.nasa.gov/planets/eph_export.html)

- Hipparchus Catalogue

  [The Hipparcos and Tycho Catalogues](https://www.cosmos.esa.int/web/hipparcos/catalogues)
  [FTP](https://cdsarc.cds.unistra.fr/ftp/cats/I/239) (DE406)

- Bayer Designation and Proper Name

  [FTP](https://cdsarc.cds.unistra.fr/ftp/I/239/version_cd/tables) (ident4, ident6)

- Timezone

  [Timezone Boundary Builder](https://github.com/evansiroky/timezone-boundary-builder)

## References

- [IMCCE, Paris Observatory](https://www.imcce.fr)

- [Rise, Set, and Twilight Definitions](https://aa.usno.navy.mil/faq/RST_defs)

- R. Tousey and M. J. Koomen, "The Visibility of Stars and Planets During Twilight," *Journal of the Optical Society of America*, Vol. 43, pp. 177-183, 1953. [Online]. Available: <https://opg.optica.org/josa/viewmedia.cfm?uri=josa-43-3-177&seq=0&html=true>
