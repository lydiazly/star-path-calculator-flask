# -*- coding: utf-8 -*-
# core/seasons.py
"""Functions to calculate the time and coordinates of equinoxes and solstices.

Refer to the global variables `eph`, `earth`, and `timescale` by:
>>> import spcalc.core.data_loader as dl
>>> eph = dl.eph
>>> earth = dl.earth
>>> timescale = dl.timescale
"""

import numpy as np
from numpy.typing import NDArray
from skyfield.almanac import find_discrete, seasons
from skyfield.timelib import Time

import spcalc.core.data_loader as dl

__all__ = ["get_coords", "get_seasons"]

timescale = dl.timescale

# Ensure ephemeris data is loaded
if dl.eph is None or dl.earth is None:
    dl.load_data()
    # print("Warning: Ephemeris data was not loaded. `core.data_loader.load_data()` is called.")


def get_coords(year: int) -> dict[str, float | tuple[int | float, ...]]:
    """Calculates the times and coordinates of equinoxes and solstices for the given year.
    - The derived positions are adjusted for light-time delay.
        Reference: https://rhodesmill.org/skyfield/api-position.html#skyfield.positionlib.Barycentric.observe

    Args:
        year (int): The year in Gregorian calendar. 0 is 1 BCE.

    Returns:
        dict: A dictionary containing the times and ICRS coordinates of equinoxes and solstices:
            {
                'vernal_ra': float,
                'vernal_dec': float,
                'summer_ra': float,
                'summer_dec': float,
                'autumnal_ra': float,
                'autumnal_dec': float,
                'winter_ra': float,
                'winter_dec': float,
                'vernal_time': tuple[int | float, ...],
                'summer_time': tuple[int | float, ...],
                'autumnal_time': tuple[int | float, ...],
                'winter_time': tuple[int | float, ...],
            }
    """
    t0: Time = timescale.ut1(year, 1, 1, 0, 0, 0)
    t1: Time = timescale.ut1(year + 1, 1, 1, 0, 0, 0)

    # Find the times of the seasons
    ts: Time
    events: NDArray[np.int64]
    ts, events = find_discrete(t0, t1, seasons(dl.eph))

    # Calculate the ICRS coordinates of the sun at those times
    sun = dl.eph['sun']  # type: ignore[index]

    coord_icrs = []
    for ti in ts:
        astrometric = dl.earth.at(ti).observe(sun)  # type: ignore[union-attr]
        ra_icrs, dec_icrs, _ = astrometric.radec()
        coord_icrs.append([ra_icrs._degrees, dec_icrs._degrees])

    _vernal_time, _summer_time, _autumnal_time, _winter_time = [
        ti.ut1_calendar() for ti in ts
    ]

    results: dict[str, float | tuple[int | float, ...]] = {
        'vernal_ra': float(coord_icrs[0][0]),
        'vernal_dec': float(coord_icrs[0][1]),
        'summer_ra': float(coord_icrs[1][0]),
        'summer_dec': float(coord_icrs[1][1]),
        'autumnal_ra': float(coord_icrs[2][0]),
        'autumnal_dec': float(coord_icrs[2][1]),
        'winter_ra': float(coord_icrs[3][0]),
        'winter_dec': float(coord_icrs[3][1]),
        'vernal_time': (*map(int, _vernal_time[:5]), float(_vernal_time[-1])),
        'summer_time': (*map(int, _summer_time[:5]), float(_summer_time[-1])),
        'autumnal_time': (*map(int, _autumnal_time[:5]), float(_autumnal_time[-1])),
        'winter_time': (*map(int, _winter_time[:5]), float(_winter_time[-1])),
    }

    return results


def get_seasons(year: int) -> dict[str, tuple[int | float, ...]]:
    """Calculates the times of equinoxes and solstices for the given year.

    Args:
        year (int): The year in Gregorian calendar. 0 is 1 BCE.

    Returns:
        dict: A dictionary containing the times of equinoxes and solstices:
            {
                'vernal_time': tuple[int | float, ...],
                'summer_time': tuple[int | float, ...],
                'autumnal_time': tuple[int | float, ...],
                'winter_time': tuple[int | float, ...],
            }
    """
    t0: Time = timescale.ut1(year, 1, 1, 0, 0, 0)
    t1: Time = timescale.ut1(year + 1, 1, 1, 0, 0, 0)

    # Find the times of the seasons
    ts: Time
    events: NDArray[np.int64]
    ts, events = find_discrete(t0, t1, seasons(dl.eph))
    _vernal_time, _summer_time, _autumnal_time, _winter_time = [
        ti.ut1_calendar() for ti in ts
    ]

    results: dict[str, tuple[int | float, ...]] = {
        'vernal_time': (*map(int, _vernal_time[:5]), float(_vernal_time[-1])),
        'summer_time': (*map(int, _summer_time[:5]), float(_summer_time[-1])),
        'autumnal_time': (*map(int, _autumnal_time[:5]), float(_autumnal_time[-1])),
        'winter_time': (*map(int, _winter_time[:5]), float(_winter_time[-1])),
    }

    return results


def plot_ve_ra(year_start: int, year_end: int, step: int = 1) -> None:
    """Plots the right ascensions of vernal equinoxes from `year_start` to `year_end`."""
    import matplotlib.pyplot as plt

    year_list = list(range(year_start, year_end + 1, step))
    ra_list = [get_coords(y)['vernal_ra'] * 3600 for y in year_list]

    coefficients = np.polyfit(year_list, ra_list, 1)

    plt.figure()
    plt.plot(year_list, ra_list - np.poly1d(coefficients)(year_list))
    plt.show()
