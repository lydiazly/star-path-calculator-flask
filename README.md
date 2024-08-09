# PlotStarTrail

[![python](https://img.shields.io/badge/Python-3.10,_3.11-3776AB?logo=python&logoColor=white)](https://www.python.org) [![numpy](https://img.shields.io/badge/Numpy-2.0.1-013243?logo=numpy&logoColor=white)](https://numpy.org) [![pandas](https://img.shields.io/badge/Pandas-2.2.2-150458?logo=Pandas&logoColor=white)](https://pandas.pydata.org) [![matplotlib](https://img.shields.io/badge/Matplotlib-3.9.1.post1-12557C)](https://matplotlib.org) [![skyfield](https://img.shields.io/badge/Skyfield-1.49-BD9354)](https://rhodesmill.org/skyfield) [![juliandate](https://img.shields.io/badge/Juliandate-1.0.4-BD9354)](https://pypi.org/project/juliandate) [![tzfpy](https://img.shields.io/badge/tzfpy-0.15.5-blue)](https://github.com/ringsaturn/tzfpy)

[Website](https://lydiazly.github.io/star-trail-viewer)

[Flask server](https://github.com/lydiazly/equinox-coord-flask)

[React app](https://github.com/lydiazly/star-trail-viewer)

## Table of Contents<!-- omit in toc -->

- [Overview](#overview)
- [Features](#features)
- [Install](#install)
- [Usage](#usage)
  - [get\_equinoxes\_solstices.py](#get_equinoxes_solsticespy)
  - [get\_star\_trail.py](#get_star_trailpy)

## Overview

<!-- TODO -->

We are aiming to develop a user-friendly app to facilitate the research in history of astronomy, providing a convenient approach to help researchers get important astronomical information in the past.

## Features

<!-- TODO -->

The first function of this app is to calculate the ICRS coordinates of two equinoxes and two solstices from several thousand years ago to several thousand years later.

## Install

```sh
python3 -m pip install pandas matplotlib skyfield juliandate tzfpy
```

## Usage

### [get_equinoxes_solstices.py](./scripts/get_equinoxes_solstices.py)

Example:

```bash
python3 ./scripts/get_equinoxes_solstices.py -2000
```

Output:

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

Usage:

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

### [get_star_trail.py](./scripts/get_star_trail.py)

Example:

```bash
python3 ./scripts/get_equinoxes_solstices.py -2000
```

Output:

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

Usage:

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
