# -*- coding: utf-8 -*-
# core/coordinates.py
"""
Functions to calculate the coordinates of equinoxes and solstices.

Use global variables eph and earth by referencing, e.g.:
```
import core.data_loader as dl
some_value = dl.eph.some_method()
```
"""

from typing import Tuple
from skyfield.api import load, Star, Angle, Timescale
from skyfield.framelib import ecliptic_frame
from scipy.optimize import root
import core.data_loader as dl

__all__ = ["get_coords",]


if dl.eph is None:
    dl.load_data()
    # print("Warning: Ephemeris data was not loaded. `core.data_loader.load_data()` is called.")


# The basic idea of determining the ICRS coordinates of equinoxes of a date is to
# find the points with the ecliptic coordinates of (0,0) and (180,0).
# For solstices, the idea is to find the points with the ecliptic coordinates
# of (90,0) and (270,0).
def get_ecliptic_coord(positions_j2000, ts: Timescale) -> Tuple[Angle]:
    ra_j2000, dec_j2000 = positions_j2000
    star = Star(ra_hours=ra_j2000/15, dec_degrees=dec_j2000)
    position = dl.earth.at(ts).observe(star)
    lat, lon, _ = position.frame_latlon(ecliptic_frame)
    return (lat.degrees, lon._degrees)


def coord_for_equinoxes(positions_j2000, ts: Timescale) -> Tuple[Angle]:
    a, b = get_ecliptic_coord(positions_j2000, ts)
    return (a, b-180)


def coord_for_solstices(positions_j2000, ts: Timescale) -> Tuple[Angle]:
    a, b = get_ecliptic_coord(positions_j2000, ts)
    return (a, b-90)


def get_equinoxes(ts: Timescale) -> Tuple[Angle]:
    sol = root(coord_for_equinoxes, x0=[180,0], args=(ts), method='lm', tol=1e-8)
    x1 = sol.x[0]
    x2 = sol.x[1]
    autumnal_ra_j2000 = Angle(hours=x1/15)
    autumnal_dec_j2000 = Angle(degrees=x2)
    if x1 - 180 >= 0:
        vernal_ra_j2000 = Angle(hours=(x1 - 180)/15)
    else:
        vernal_ra_j2000 = Angle(hours=(x1 + 180)/15)
    vernal_dec_j2000 = Angle(degrees=-x2)
    return (vernal_ra_j2000, vernal_dec_j2000, autumnal_ra_j2000, autumnal_dec_j2000)


def get_solstices(ts: Timescale) -> Tuple[Angle]:
    sol = root(coord_for_solstices, x0=[90,0], args=(ts), method='lm', tol=1e-8)
    x1 = sol.x[0]
    x2 = sol.x[1]
    summer_ra_j2000 = Angle(hours=x1/15)
    summer_dec_j2000 = Angle(degrees=x2)
    winter_ra_j2000 = Angle(hours=(x1 + 180)/15)
    winter_dec_j2000 = Angle(degrees=-x2)
    return (summer_ra_j2000, summer_dec_j2000, winter_ra_j2000, winter_dec_j2000)


def get_coords(year: int, month: int = 1, day: int = 1,
               hour: int = 12, minute: int = 0, second: float = 0, *args) -> dict:
    ts = load.timescale()
    t = ts.ut1(year, month, day, hour, minute, second)
    # print([year, month, day, hour, minute, second])

    vernal_ra_j2000, vernal_dec_j2000, autumnal_ra_j2000, autumnal_dec_j2000 = get_equinoxes(t)
    summer_ra_j2000, summer_dec_j2000, winter_ra_j2000, winter_dec_j2000 = get_solstices(t)

    results = {
        'vernal_ra': str(vernal_ra_j2000), 'vernal_dec': str(vernal_dec_j2000),
        'autumnal_ra': str(autumnal_ra_j2000), 'autumnal_dec': str(autumnal_dec_j2000),
        'summer_ra': str(summer_ra_j2000), 'summer_dec': str(summer_dec_j2000),
        'winter_ra': str(winter_ra_j2000), 'winter_dec': str(winter_dec_j2000),
    }

    return results
