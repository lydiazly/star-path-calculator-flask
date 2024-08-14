# Stardial - Flask

[![python](https://img.shields.io/badge/Python-3.10,_3.11-3776AB?logo=python&logoColor=white)](https://www.python.org) [![numpy](https://img.shields.io/badge/Numpy-2.0.1-013243?logo=numpy&logoColor=white)](https://numpy.org) [![pandas](https://img.shields.io/badge/Pandas-2.2.2-150458?logo=Pandas&logoColor=white)](https://pandas.pydata.org) [![matplotlib](https://img.shields.io/badge/Matplotlib-3.9.1.post1-12557C)](https://matplotlib.org) [![skyfield](https://img.shields.io/badge/Skyfield-1.49-BD9354)](https://rhodesmill.org/skyfield) [![juliandate](https://img.shields.io/badge/Juliandate-1.0.4-BD9354)](https://pypi.org/project/juliandate) [![tzfpy](https://img.shields.io/badge/tzfpy-0.15.5-blue)](https://github.com/ringsaturn/tzfpy) [![great-circle-calculator](https://img.shields.io/badge/Great_Circle_Calculator-1.3.1-brightgreen)](https://github.com/seangrogan/great_circle_calculator) [![Flask](https://img.shields.io/badge/Flask-3.0.3-39A6BD?logo=flask&logoColor=white)](https://flask.palletsprojects.com)

A RESTFul Flask server based on [this project](https://github.com/claude-hao/equinox-coord).

## Endpoints

### 1. Get dates, times, and coordinates in RA and Dec for the equinoxes and solstices of a given year

`https://equinoxcoord.pythonanywhere.com/seasons`

Parameters:

- `year`: (*required*) a year in the range of (-3000, 3000). Note that *0* is *1 BCE*
- `tz`: a timezone identifier, e.g., `tz=Asia%2FShanghai`
- `lat`: the latitude in decimal degrees
- `lng`: the longitude in decimal degrees

If `tz` is not provided, `lat` and `lng` must be specified. If `tz`, `lat`, and `lng` are given together, only the value of `tz` will be used.

Returns:

- `results`: a list of all the obtained coordinates and times of the equinoxes and solstices

### 2. Get only the date of one of the equinoxes and solstices

`https://equinoxcoord.pythonanywhere.com/equinox`

Parameters:

- `year`: (*required*) same as above
- `tz`: same as above
- `lat`: same as above
- `lng`: same as above
- `flag`: (*required*)
  - `flag=ve`: Vernal Equinox
  - `flag=ss`: Summer Solstice
  - `flag=ae`: Autumnal Equinox
  - `flag=ws`: Winter Solstice

Returns:

- `results`: a list of the obtained coordinates and times of the specified equinox or solstice

### 3. Plot the path of a celestial object on a local date at a specified location

`https://equinoxcoord.pythonanywhere.com/diagram`

Parameters:

- `year`: (*required*) same as above
- `month`: (*required*) a month as a number (from 1 to 12).
- `day`: (*required*) a day of the month.
- `tz`: same as above
- `lat`: same as above
- `lng`: same as above
- `flag`: (*required*) same as above
- `cal`: (*required*) calendar
  - `cal=` or not provided: Gregorian calendar
  - `cal=j`: Julian calendar

Returns:

- `name`: if `hip` is specified, finds and returns the corresponding proper name or the Bayer designation
- `diagramId`: a string of a unix timestamp
- `svgData`: the plotted SVG data
- `annotations`: a list of details of the points on the figure

## Install

```sh
python3 -m pip install pandas matplotlib skyfield juliandate tzfpy Flask
```

## Run the Flask app locally in development mode

```sh
python3 run.py
```

The server will be running on <https://localhost:5001>
