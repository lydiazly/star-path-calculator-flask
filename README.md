# Star Path Calculator - Flask

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![python](https://img.shields.io/badge/Python-3.11,3.12-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![numpy](https://img.shields.io/badge/Numpy-2.4.4-013243?logo=numpy&logoColor=white)](https://numpy.org)
[![pandas](https://img.shields.io/badge/Pandas-3.0.2-150458?logo=Pandas&logoColor=white)](https://pandas.pydata.org)
[![matplotlib](https://img.shields.io/badge/Matplotlib-3.10.8-12557C)](https://matplotlib.org)
[![skyfield](https://img.shields.io/badge/Skyfield-1.54-BD9354)](https://rhodesmill.org/skyfield)
[![juliandate](https://img.shields.io/badge/Juliandate-1.0.5-BD9354)](https://pypi.org/project/juliandate)
[![tzfpy](https://img.shields.io/badge/tzfpy-1.3.1-blue)](https://github.com/ringsaturn/tzfpy)
[![great-circle-calculator](https://img.shields.io/badge/Great_Circle_Calculator-1.3.1-brightgreen)](https://github.com/seangrogan/great_circle_calculator)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-39A6BD?logo=flask&logoColor=white)](https://flask.palletsprojects.com)

The Flask server of our [Star Path Viewer](https://starpathviewer.cc/) website.

[→ Team: Stardial](https://github.com/stardial-astro)

[→ Source code](https://github.com/claude-hao/star-path-calculator)

[→ React app](https://github.com/stardial-astro/star-path-viewer)

## Table of Contents<!-- omit in toc -->

- [Endpoints](#endpoints)
  - [1. Seasons](#1-seasons)
  - [2. Equinoxes and Solstices](#2-equinoxes-and-solstices)
  - [3. Diagram](#3-diagram)

## Endpoints

Base URL: <https://starpathcalculator.pythonanywhere.com>

### 1. Seasons

Get dates, times, and and RA/Dec coordinates of equinoxes and solstices by specifying a year and a location.

`/seasons`

Parameters:

- `year`: (*required*) a year from -2999 to 2999. 0 is 1 BCE.
- `tz`: (*required*) IANA time zone ID, e.g., `tz=Asia%2FShanghai`.
- `lat`: latitude in decimal degrees.
- `lng`: longitude in decimal degrees.

If `tz` is not provided, `lat` and `lng` must be specified. If `tz`, `lat`, and `lng` are given together, only the value of `tz` will be used.

Returns:

- `results`: JSON formatted data contains all the obtained coordinates and times of the equinoxes and solstices.

Example:

`/seasons?tz=Etc%2FGMT&year=-1000`

```json
{
  "results": {
    "autumnal_dec": -15.5640130948836,
    "autumnal_ra": 219.114596206919,
    "autumnal_time": [-1000, 9, 23, 7, 15, 44.1148616373539],
    "summer_dec": 17.5909755740231,
    "summer_ra": 134.184027102195,
    "summer_time": [-1000, 6, 23, 16, 9, 1.93309620022774],
    "vernal_dec": 15.5661277766416,
    "vernal_ra": 39.1204852333523,
    "vernal_time": [-1000, 3, 21, 10, 8, 34.8072123527527],
    "winter_dec": -17.592567254477,
    "winter_ra": 314.177991317744,
    "winter_time": [-1000, 12, 20, 17, 23, 41.1424760520458]
  },
  "tz": "Etc/GMT",
  "tzname": "GMT",
  "year": -1000
}
```

### 2. Equinoxes and Solstices

Get only the date of one of the equinoxes and solstices.

`/equinox`

Parameters:

- `year`: (*required*) same as above.
- `tz`: (*required*) same as above.
- `lat`: same as above.
- `lng`: same as above.
- `flag`: (*required*) season flag.
  - `flag=ve`: vernal equinox (March equinox).
  - `flag=ss`: summer solstice (June solstice).
  - `flag=ae`: autumnal equinox (September equinox).
  - `flag=ws`: winter solstice (December solstice).

Returns:

- `results`: JSON formatted data contains the obtained coordinates and times of the specified equinox or solstice.

Example:

`/equinox?tz=Etc%2FGMT&year=-1000&flag=ve`

```json
{
  "results": [-1000, 3, 21, 10, 8, 34.8072123527527],
  "tz": "Etc/GMT",
  "tzname": "GMT",
  "year": -1000
}
```

### 3. Diagram

Plot the star path and calculates the times and target positions of rising/setting/transit and twilights.

`/diagram`

Parameters:

- `year`: (*required*) same as above.
- `month`: (*required*) month as a number (from 1 to 12).
- `day`: (*required*) day of the month.
- `lat`: (*required*) same as above.
- `lng`: (*required*) same as above.
- `name` | `hip` | `ra`, `dec`: (*required*) either a planet name (case insensitive), Hipparcos Catalogue number, or a RA/Dec pair.
- `tz`: the time zone ID of this location.
- `cal`: the calendar flag.
  - `cal=` or not provided: Gregorian calendar.
  - `cal=j`: Julian calendar.

If `tz` is not provided, it will be derived from the `lat` and `lng`.
Specifying `tz` can enhance speed. However, if `tz` doesn't match the `lat` and `lng`, the result will be incorrect. To optimize performance, we do not verify this match.

Returns:

- `diagramId`: a string of a unix timestamp.
- `offset`: time zone offset in decimal hours.
- `svgData`: the Base64-encoded SVG data of the output figure.
- `annotations`: a list of details about the points on the figure, including dates in both the Gregorian and Julian calendars.
- `tz`: the time zone ID of this location.
- `tzname`: the time zone name of this location.
- `date_cc`: the Chinese calendar date object.
