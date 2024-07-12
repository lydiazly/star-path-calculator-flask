# EquinoxCoord - Flask

[![python](https://img.shields.io/badge/Python-3.10,_3.11-3776AB?logo=python&logoColor=white)](https://www.python.org) [![scipy](https://img.shields.io/badge/SciPy-1.14.0-8CAAE6?logo=scipy&logoColor=white)](https://scipy.org) [![skyfield](https://img.shields.io/badge/skyfield-1.49-BD9354)](https://rhodesmill.org/skyfield) [![Flask](https://img.shields.io/badge/Flask-3.0.3-39A6BD?logo=flask&logoColor=white)](https://flask.palletsprojects.com)

A Flask [demo website](https://equinoxcoord.pythonanywhere.com/) of [EquinoxCoord](https://github.com/claude-hao/equinox-coord.git).

## Usage

- Run the Flask app locally in development mode

```sh
python3 -m pip install scipy skyfield Flask
python3 run.py
```

- Use the script to get the coordinates (same as in [EquinoxCoord](https://github.com/claude-hao/equinox-coord.git))

```sh
python3 -m pip install scipy skyfield
```

```bash
python3 get_equinoxes_solstices.py 2000

# ICRS coordinates (J2000) of equinoxes and solstices on 1 Jan 2000 CE, at 12:00:00:
# Vernal Equinox:
#   ra = 00h 00m 00.85s, dec = 00deg 00' 05.6"
# Autumnal Equinox:
#   ra = 12h 00m 00.85s, dec = -00deg 00' 05.6"
# Summer solstice:
#   ra = 06h 00m 01.01s, dec = 23deg 26' 21.4"
# Winter solstice:
#   ra = 18h 00m 01.01s, dec = -23deg 26' 21.4"
```

```bash
python3 get_equinoxes_solstices.py -h

# usage: python get_equinoxes_solstices.py [-h] [-t [time]] [year] [month] [day]

# Specify a date between 29 Jan 3001 BCE and 6 May 3000 CE) to get the coordinates. The default time is 12:00:00.

# positional arguments:
#   year        int, 0 is 1 BCE (default: this year)
#   month       e.g., January|Jan|1 (default: this month or January if year is provided)
#   day         int, (default: today or 1 if year is provided)

# options:
#   -h, --help  show this help message and exit
#   -t [time]   hh|hh:mm|hh:mm:ss, 24-hour format (default: 12:00:00)

# date range:
#   29 Jan 3001 BCE -- 6 May 3000 CE
# examples:
#   # The current coordinates:
#   python get_equinoxes_solstices.py

#   # The coordinates on 1 Jan 3001 BCE, at 12:00:00:
#   python get_equinoxes_solstices.py -3000

#   # The coordinates on 1 Feb 3001 BCE, at 21:00:00:
#   python get_equinoxes_solstices.py -3000 2 1 -t 21:00:00
```
