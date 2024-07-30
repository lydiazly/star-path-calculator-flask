# EquinoxCoord - Flask

[![python](https://img.shields.io/badge/Python-3.10,_3.11-3776AB?logo=python&logoColor=white)](https://www.python.org) [![numpy](https://img.shields.io/badge/Numpy-2.0.0-013243?logo=numpy&logoColor=white)](https://numpy.org/) [![scipy](https://img.shields.io/badge/SciPy-1.14.0-8CAAE6?logo=scipy&logoColor=white)](https://scipy.org) [![pandas](https://img.shields.io/badge/Pandas-2.2.2-150458?logo=Pandas&logoColor=white)](https://pandas.pydata.org/) [![skyfield](https://img.shields.io/badge/Skyfield-1.49-BD9354)](https://rhodesmill.org/skyfield) [![juliandate](https://img.shields.io/badge/Juliandate-1.0.4-BD9354)](https://pypi.org/project/juliandate/) [![adjusttext](https://img.shields.io/badge/adjustText-1.2.0-8ED500)](https://github.com/Phlya/adjustText) [![timezonefinder](https://img.shields.io/badge/timezonefinder-6.5.2-blue)](https://github.com/jannikmi/timezonefinder) [![Flask](https://img.shields.io/badge/Flask-3.0.3-39A6BD?logo=flask&logoColor=white)](https://flask.palletsprojects.com)

A Flask [demo website](https://equinoxcoord.pythonanywhere.com/) of [EquinoxCoord](https://github.com/claude-hao/equinox-coord.git).

## Usage

- Run the Flask app locally in development mode

```sh
python3 -m pip install adjusttext juliandate pandas pytz scipy skyfield timezonefinder Flask
python3 run.py
```

- Use the script to get the equinoxes and solstices (same as in [EquinoxCoord](https://github.com/claude-hao/equinox-coord.git))

```sh
python3 -m pip install adjusttext juliandate pandas pytz scipy skyfield timezonefinder
```

Example:

```bash
python3 get_equinoxes_solstices.py -2000
```

Output:

```text
Dates, times, and ICRS coordinates (J2000) for the equinoxes and solstices of 2001 BCE:

[Vernal Equinox] -2000-03-21 04:40:19.602 (UT1)
  ra = 52.962, dec = 19.517

[Summer Solstice] -2000-06-23 11:32:34.141 (UT1)
  ra = 147.791, dec = 13.371

[Autumnal Equinox] -2000-09-22 05:50:58.094 (UT1)
  ra = 232.955, dec = -19.515

[Winter Solstice] -2000-12-19 15:18:26.852 (UT1)
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
  -3000-01-29 – 3000-05-06 (UT1)
examples:
  # The current year:
  python get_equinoxes_solstices.py

  # The equinoxes and solstices of 2001 BCE:
  python get_equinoxes_solstices.py -2000
```
