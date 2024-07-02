# app/utils.py
from skyfield.api import load, Star, Angle
from skyfield.framelib import ecliptic_frame
# import numpy as np
from scipy.optimize import root


# Load the ephemeris data
DATA_FILE = 'de406.bsp'
eph = load(DATA_FILE)
earth = eph['earth']


# The basic idea of determining the ICRS coordinates of equinoxes of date is to
# find the points which have the of-date ecliptic coordinates of (0,0), (180,0).
# For solstices, it is to
# find the points which have the of-date ecliptic coordinates of (90,0), (270,0).
def get_ecliptic_coord(positions_j2000, ts):
    ra_j2000, dec_j2000 = positions_j2000
    star = Star(ra_hours=ra_j2000/15, dec_degrees=dec_j2000)
    position = earth.at(ts).observe(star)
    lat, lon, _ = position.frame_latlon(ecliptic_frame)
    return [lat.degrees, lon._degrees]


def used_for_equinoxes(positions_j2000, ts):
    a, b = get_ecliptic_coord(positions_j2000, ts)
    return [a, b-180]


def used_for_solstices(positions_j2000, ts):
    a, b = get_ecliptic_coord(positions_j2000, ts)
    return [a, b-90]


def get_equinoxes(ts):
    sol = root(used_for_equinoxes, x0=[180,0], args=(ts), method='lm', tol=1e-8)
    x1 = sol.x[0]
    x2 = sol.x[1]
    autumnal_ra_j2000 = Angle(hours=x1/15)
    autumnal_dec_j2000 = Angle(degrees=x2)
    if x1 - 180 >= 0:
        vernal_ra_j2000 = Angle(hours=(x1 - 180)/15)
    else:
        vernal_ra_j2000 = Angle(hours=(x1 + 180)/15)
    vernal_dec_j2000 = Angle(degrees=-x2)
    return [vernal_ra_j2000, vernal_dec_j2000, autumnal_ra_j2000, autumnal_dec_j2000]


def get_solstices(ts):
    sol = root(used_for_solstices, x0=[90,0], args=(ts), method='lm', tol=1e-8)
    x1 = sol.x[0]
    x2 = sol.x[1]
    summer_ra_j2000 = Angle(hours=x1/15)
    summer_dec_j2000 = Angle(degrees=x2)
    winter_ra_j2000 = Angle(hours=(x1 + 180)/15)
    winter_dec_j2000 = Angle(degrees=-x2)
    return [summer_ra_j2000, summer_dec_j2000, winter_ra_j2000, winter_dec_j2000]
