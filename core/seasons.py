# -*- coding: utf-8 -*-
# core/seasons.py
"""
Functions to calculate the time and coordinates of equinoxes and solstices.

Use global variables eph and earth by referencing, e.g.:
```
import core.data_loader as dl
some_value = dl.eph.some_method()
```
"""

from skyfield.api import load
from skyfield.almanac import find_discrete, seasons
import core.data_loader as dl

__all__ = ["get_coords", "get_seasons"]


# Ensure ephemeris data is loaded
if dl.eph is None or dl.earth is None:
    dl.load_data()
    # print("Warning: Ephemeris data was not loaded. `core.data_loader.load_data()` is called.")


def get_coords(year: int) -> dict:
    """
    Calculates the times and coordinates of equinoxes and solstices for the given year.

    Args:
        year (int): The year in Gregorian calendar.

    Returns:
        dict: A dictionary containing the times and ICRS coordinates of equinoxes and solstices.
        The derived positions are adjusted for light-time delay
        (https://rhodesmill.org/skyfield/api-position.html#skyfield.positionlib.Barycentric.observe).
    """

    tisca = load.timescale()
    t0 = tisca.ut1(year, 1, 1, 0, 0, 0)
    t1 = tisca.ut1(year + 1, 1, 1, 0, 0, 0)

    # Find the times of the seasons
    ts, ys = find_discrete(t0, t1, seasons(dl.eph))

    # Calculate the ICRS coordinates of the sun at those times
    sun = dl.eph['sun']

    coord_icrs = []
    for ti in ts:
        astrometric = dl.earth.at(ti).observe(sun)
        ra_icrs, dec_icrs, _ = astrometric.radec()
        coord_icrs.append([ra_icrs._degrees, dec_icrs._degrees])

    _vernal_time, _summer_time, _autumnal_time, _winter_time = [ti.ut1_calendar() for ti in ts]

    results = {
        'vernal_ra': float(coord_icrs[0][0]), 'vernal_dec': float(coord_icrs[0][1]),
        'summer_ra': float(coord_icrs[1][0]), 'summer_dec': float(coord_icrs[1][1]),
        'autumnal_ra': float(coord_icrs[2][0]), 'autumnal_dec': float(coord_icrs[2][1]),
        'winter_ra': float(coord_icrs[3][0]), 'winter_dec': float(coord_icrs[3][1]),
        'vernal_time': (*map(int, _vernal_time[:5]), float(_vernal_time[-1])),
        'summer_time': (*map(int, _summer_time[:5]), float(_summer_time[-1])),
        'autumnal_time': (*map(int, _autumnal_time[:5]), float(_autumnal_time[-1])),
        'winter_time': (*map(int, _winter_time[:5]), float(_winter_time[-1]))
    }

    return results


def get_seasons(year: int) -> dict:
    """
    Calculates the times of equinoxes and solstices for the given year.

    Args:
        year (int): The year in Gregorian calendar.

    Returns:
        dict: A dictionary containing the times of equinoxes and solstices.
    """

    tisca = load.timescale()
    t0 = tisca.ut1(year, 1, 1, 0, 0, 0)
    t1 = tisca.ut1(year + 1, 1, 1, 0, 0, 0)

    # Find the times of the seasons
    ts, ys = find_discrete(t0, t1, seasons(dl.eph))
    _vernal_time, _summer_time, _autumnal_time, _winter_time = [ti.ut1_calendar() for ti in ts]

    results = {
        'vernal_time': (*map(int, _vernal_time[:5]), float(_vernal_time[-1])),
        'summer_time': (*map(int, _summer_time[:5]), float(_summer_time[-1])),
        'autumnal_time': (*map(int, _autumnal_time[:5]), float(_autumnal_time[-1])),
        'winter_time': (*map(int, _winter_time[:5]), float(_winter_time[-1]))
    }

    return results


def plot_ve_ra(year_start, year_end, step=1):
    """Plots the right ascensions of vernal equinoxes from `year_start` to `year_end`."""
    import numpy as np
    import matplotlib.pyplot as plt

    year_list = list(range(year_start, year_end+1, step))
    ra_list = [get_coords(y)['vernal_ra']*3600 for y in year_list]

    coefficients = np.polyfit(year_list, ra_list, 1)

    plt.figure()
    plt.plot(year_list, ra_list - np.poly1d(coefficients)(year_list))
    plt.show()
