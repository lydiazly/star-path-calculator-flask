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

# The ICRS coordinates (J2000) of equinoxes and solstices in the year 2000 are:
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

# usage: get_equinoxes_solstices.py [-h] [year]

# positional arguments:
#   year        Format: yyyy (default: current year)

# options:
#   -h, --help  show this help message and exit
```
