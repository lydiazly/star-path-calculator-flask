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

from typing import Tuple
import numpy as np
from skyfield.api import load
from skyfield.almanac import find_discrete, seasons
import core.data_loader as dl

__all__ = ["get_coords",]


if dl.eph is None:
    dl.load_data()
    # print("Warning: Ephemeris data was not loaded. `core.data_loader.load_data()` is called.")


def get_coords(year: int, month: int = 1, day: int = 1,
               hour: int = 12, minute: int = 0, second: float = 0, *args) -> dict:
    """
    The input year is the year in Gregorian calendar.
    """

    tisca = load.timescale()
    t0 = tisca.ut1(year, 1, 1, 0, 0, 0)
    t1 = tisca.ut1(year+1, 1, 1, 0, 0, 0)

    ts, ys = find_discrete(t0, t1, seasons(dl.eph))

    sun = dl.eph['sun']
    coord_j2000 = np.zeros(shape=(0,2), dtype=float)
    for ti in ts:
        astrometric = dl.earth.at(ti).observe(sun)
        ra_j2000, dec_j2000, _ = astrometric.radec()
        coord_j2000 = np.append(coord_j2000, [[ra_j2000._degrees, dec_j2000._degrees]], axis=0)

    results = {
        'vernal_ra': str(coord_j2000[0,0]), 'vernal_dec': str(coord_j2000[0,1]),
        'summer_ra': str(coord_j2000[1,0]), 'summer_dec': str(coord_j2000[1,1]),
        'autumnal_ra': str(coord_j2000[2,0]), 'autumnal_dec': str(coord_j2000[2,1]),
        'winter_ra': str(coord_j2000[3,0]), 'winter_dec': str(coord_j2000[3,1]),
        'vernal_time': ts[0].ut1_calendar(),
        'summer_time': ts[1].ut1_calendar(),
        'autumnal_time': ts[2].ut1_calendar(),
        'winter_time': ts[3].ut1_calendar()
    }

    return results
