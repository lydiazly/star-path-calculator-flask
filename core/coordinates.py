# -*- coding: utf-8 -*-
# core/coordinates.py
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
    Calculate the time and coordinates of equinoxes and solstices for the given year.

    Parameters:
        year (int): The year in Gregorian calendar.

    Returns:
        dict: A dictionary containing the times and coordinates of equinoxes and solstices.
    """

    tisca = load.timescale()
    t0 = tisca.ut1(year, 1, 1, 0, 0, 0)
    t1 = tisca.ut1(year + 1, 1, 1, 0, 0, 0)

    # Find the times of the seasons
    ts, ys = find_discrete(t0, t1, seasons(dl.eph))

    # Calculate the J2000 coordinates of the sun at those times
    sun = dl.eph['sun']

    # coord_j2000 = np.zeros(shape=(0,2), dtype=float)
    # for ti in ts:
    #     astrometric = dl.earth.at(ti).observe(sun)
    #     ra_j2000, dec_j2000, _ = astrometric.radec()
    #     coord_j2000 = np.append(coord_j2000, [[ra_j2000._degrees, dec_j2000._degrees]], axis=0)

    coord_j2000 = []
    for ti in ts:
        astrometric = dl.earth.at(ti).observe(sun)
        ra_j2000, dec_j2000, _ = astrometric.radec()
        coord_j2000.append([ra_j2000._degrees, dec_j2000._degrees])

    # _vernal_time = ts[0].ut1_calendar()
    # _summer_time = ts[1].ut1_calendar()
    # _autumnal_time = ts[2].ut1_calendar()
    # _winter_time = ts[3].ut1_calendar()
    _vernal_time, _summer_time, _autumnal_time, _winter_time = [ti.ut1_calendar() for ti in ts]

    results = {
        'vernal_ra': float(coord_j2000[0][0]), 'vernal_dec': float(coord_j2000[0][1]),
        'summer_ra': float(coord_j2000[1][0]), 'summer_dec': float(coord_j2000[1][1]),
        'autumnal_ra': float(coord_j2000[2][0]), 'autumnal_dec': float(coord_j2000[2][1]),
        'winter_ra': float(coord_j2000[3][0]), 'winter_dec': float(coord_j2000[3][1]),
        'vernal_time': (*map(int, _vernal_time[:5]), float(_vernal_time[-1])),
        'summer_time': (*map(int, _summer_time[:5]), float(_summer_time[-1])),
        'autumnal_time': (*map(int, _autumnal_time[:5]), float(_autumnal_time[-1])),
        'winter_time': (*map(int, _winter_time[:5]), float(_winter_time[-1]))
    }

    return results


def get_seasons(year: int) -> dict:
    """
    Calculate the time of equinoxes and solstices for the given year.

    Parameters:
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
