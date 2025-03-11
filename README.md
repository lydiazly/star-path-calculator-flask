# Star Path Calculator - Flask

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![python](https://img.shields.io/badge/Python-3.10,_3.11-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![numpy](https://img.shields.io/badge/Numpy-2.2.3-013243?logo=numpy&logoColor=white)](https://numpy.org)
[![pandas](https://img.shields.io/badge/Pandas-2.2.3-150458?logo=Pandas&logoColor=white)](https://pandas.pydata.org)
[![matplotlib](https://img.shields.io/badge/Matplotlib-3.10.1-12557C)](https://matplotlib.org)
[![pytest](https://img.shields.io/badge/pytest-8.3.5-0A9EDC)](https://pytest.org/)
[![skyfield](https://img.shields.io/badge/Skyfield-1.49-BD9354)](https://rhodesmill.org/skyfield)
[![juliandate](https://img.shields.io/badge/Juliandate-1.0.5-BD9354)](https://pypi.org/project/juliandate)
[![tzfpy](https://img.shields.io/badge/tzfpy-0.16.4-blue)](https://github.com/ringsaturn/tzfpy)
[![great-circle-calculator](https://img.shields.io/badge/Great_Circle_Calculator-1.3.1-brightgreen)](https://github.com/seangrogan/great_circle_calculator)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-39A6BD?logo=flask&logoColor=white)](https://flask.palletsprojects.com)

The Flask server of our [Star Path Viewer](https://star-path-viewer.pages.dev/) website.

[→ Team: Stardial](https://github.com/stardial-astro)

[→ Source code](https://github.com/claude-hao/star-path-calculator)

[→ React client](https://github.com/stardial-astro/star-path-viewer)

## Table of Contents<!-- omit in toc -->

- [Endpoints](#endpoints)
  - [1. Get dates, times, and and RA/Dec coordinates of equinoxes and solstices by specifying a year and location](#1-get-dates-times-and-and-radec-coordinates-of-equinoxes-and-solstices-by-specifying-a-year-and-location)
  - [2. Get only the date of one of the equinoxes and solstices](#2-get-only-the-date-of-one-of-the-equinoxes-and-solstices)
  - [3. Plot the star path and calculates the rising/setting times and twilight stages](#3-plot-the-star-path-and-calculates-the-risingsetting-times-and-twilight-stages)

## Endpoints

### 1. Get dates, times, and and RA/Dec coordinates of equinoxes and solstices by specifying a year and location

`https://starpathcalculator.pythonanywhere.com/seasons`

Parameters:

- `year`: (*required*) a year from -2999 to 2999. 0 equals 1 BCE.
- `tz`: (*required*) a time zone identifier, e.g., `tz=Asia%2FShanghai`.
- `lat`: the latitude in decimal degrees.
- `lng`: the longitude in decimal degrees.

If `tz` is not provided, `lat` and `lng` must be specified. If `tz`, `lat`, and `lng` are given together, only the value of `tz` will be used.

Returns:

- `results`: JSON formatted data contains all the obtained coordinates and times of the equinoxes and solstices.

Example:

`https://starpathcalculator.pythonanywhere.com/seasons?tz=Etc%2FGMT&year=-1000`

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
  "year": -1000
}
```

### 2. Get only the date of one of the equinoxes and solstices

`https://starpathcalculator.pythonanywhere.com/equinox`

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

`https://starpathcalculator.pythonanywhere.com/equinox?tz=Etc%2FGMT&year=-1000&flag=ve`

```json
{
  "results": [-1000, 3, 21, 10, 8, 34.8072123527527],
  "tz": "Etc/GMT",
  "year": -1000
}
```

### 3. Plot the star path and calculates the rising/setting times and twilight stages

`https://starpathcalculator.pythonanywhere.com/diagram`

Parameters:

- `year`: (*required*) same as above.
- `month`: (*required*) month as a number (from 1 to 12).
- `day`: (*required*) day of the month.
- `lat`: (*required*) same as above.
- `lng`: (*required*) same as above.
- `name` | `hip` | `ra`, `dec`: (*required*) planet name (case insensitive), Hipparcos Catalogue number, or a RA/Dec pair.
- `tz`: the time zone identifier of this location.
- `cal`: calendar flag.
  - `cal=` or not provided: the Gregorian calendar.
  - `cal=j`: the Julian calendar.

If `tz` is not provided, it will be derived from the `lat` and `lng`.
Specifying `tz` can enhance speed. However, if `tz` doesn't match the `lat` and `lng`, the result will be incorrect. To optimize performance, we do not verify this match.

Returns:

- `diagramId`: a string of a unix timestamp.
- `offset`: time zone offset in decimal hours.
- `svgData`: the Base64-encoded SVG data of the output figure.
- `annotations`: a list of details about the points on the figure, including dates in both the Gregorian and Julian calendars.
