# EquinoxCoord

[![python](https://img.shields.io/badge/Python-3.10,_3.11-3776AB?logo=python&logoColor=white)](https://www.python.org) [![numpy](https://img.shields.io/badge/Numpy-2.0.0-013243?logo=numpy&logoColor=white)](https://numpy.org/) [![scipy](https://img.shields.io/badge/SciPy-1.14.0-8CAAE6?logo=scipy&logoColor=white)](https://scipy.org) [![skyfield](https://img.shields.io/badge/Skyfield-1.49-BD9354)](https://rhodesmill.org/skyfield) [![adjusttext](https://img.shields.io/badge/adjustText-1.2.0-8ED500)](https://github.com/Phlya/adjustText) [![timezonefinder](https://img.shields.io/badge/timezonefinder-6.5.2-blue)](https://github.com/jannikmi/timezonefinder)

A Flask [demo website](https://equinoxcoord.pythonanywhere.com/) of [EquinoxCoord](https://github.com/claude-hao/equinox-coord.git).

## Overview

We are aiming to develop a user-friendly app to facilitate the research in history of 
astronomy, providing a convenient approach to help researchers get important astronomical information
in the past.

## Features

The first function of this app is to calculate the ICRS coordinates of two equinoxes and two solstices from several thousand years ago to several thousand years later.

## Usage

- Get the coordinates

```sh
python3 -m pip install scipy skyfield
```

Example:

```bash
python3 get_equinoxes_solstices.py 2000
```

Output:

```text
ICRS coordinates (J2000) of equinoxes and solstices on 1 Jan 2000 CE, at 12:00:00:
Vernal Equinox:
  ra = 00h 00m 00.85s, dec = 00deg 00' 05.6"
Autumnal Equinox:
  ra = 12h 00m 00.85s, dec = -00deg 00' 05.6"
Summer solstice:
  ra = 06h 00m 01.01s, dec = 23deg 26' 21.4"
Winter solstice:
  ra = 18h 00m 01.01s, dec = -23deg 26' 21.4"
```

Usage:

```text
usage: python get_equinoxes_solstices.py [-h] [-t [time]] [year] [month] [day]

Specify a date and time to get the equinox and solstice coordinates in RA and DEC. The default time is 12:00:00.

positional arguments:
  year        int, 0 is 1 BCE (default: this year)
  month       e.g., January|Jan|1 (default: this month, or January if the year is provided)
  day         int, (default: today, or 1 if the year is provided)

options:
  -h, --help  show this help message and exit
  -t [time]   hh|hh:mm|hh:mm:ss, 24-hour format (default: 12:00:00)

date range:
  29 Jan 3001 BCE – 6 May 3000 CE
examples:
  # The current coordinates:
  python get_equinoxes_solstices.py

  # The coordinates on 1 Jan 3001 BCE, at 12:00:00:
  python get_equinoxes_solstices.py -3000

  # The coordinates on 5 April 3000 CE, at 21:00:00:
  python get_equinoxes_solstices.py 3000 Apr 5 -t 21
```
