# -*- coding: utf-8 -*-
# tests/test_seasons.py
import pytest
from packaging.version import Version
import skyfield
from core.seasons import get_coords, get_seasons
from .helpers import assert_dicts_equal


sig_digits = 3 if Version(skyfield.__version__) > Version('1.49') else 16

test_cases = [
    (2000,
        {
            'vernal_time': (2000, 3, 20, 7, 35, 14.617520176605467),
            'vernal_ra': 0.006200246498259485,
            'vernal_dec': 0.0027653889404899287,
            'summer_time': (2000, 6, 21, 1, 47, 42.23856749211609),
            'summer_ra': 90.00362242474856,
            'summer_dec': 23.43911265111206,
            'autumnal_time': (2000, 9, 22, 17, 27, 35.51198904926423),
            'autumnal_ra': 180.00005388448434,
            'autumnal_dec': 2.316134394620446e-05,
            'winter_time': (2000, 12, 21, 13, 37, 25.529813447887136),
            'winter_ra': 269.99658688939695,
            'winter_dec': -23.438993788457097
        }
    ),
    (2024,
        {
            'vernal_time': (2024, 3, 20, 3, 6, 24.12583535347403),
            'vernal_ra': 359.6960554164222,
            'vernal_dec': -0.13194595340307852,
            'summer_time': (2024, 6, 20, 20, 50, 59.772235641561565),
            'summer_ra': 89.63462964301416,
            'summer_dec': 23.43550816684427,
            'autumnal_time': (2024, 9, 22, 12, 43, 39.613042228687846),
            'autumnal_ra': 179.68905511595327,
            'autumnal_dec': 0.13528414596716848,
            'winter_time': (2024, 12, 21, 9, 20, 34.20657737924921),
            'winter_ra': 269.62621859461376,
            'winter_dec': -23.435556239713698
        }
    ),
]

@pytest.mark.parametrize("year, results_expected", test_cases)
def test_coords(year, results_expected):
    """Tests calculating the times and coordinates of equinoxes and solstices."""
    res = get_coords(year)
    assert_dicts_equal(res, results_expected, sig_digits=sig_digits)


@pytest.mark.parametrize("year, results_expected", test_cases)
def test_seasons(year, results_expected):
    """Tests calculating the times of equinoxes and solstices."""
    res = get_seasons(year)
    expected = {k: results_expected[k] for k in ['vernal_time', 'summer_time', 'autumnal_time', 'winter_time']}
    assert_dicts_equal(res, expected, sig_digits=sig_digits)


error_cases = [-3000, 3000]
range_error_message = r"^ephemeris segment only covers dates [-+]?[0-9]{4}-[0-9]{2}-[0-9]{2} through [-+]?[0-9]{4}-[0-9]{2}-[0-9]{2}$"

@pytest.mark.parametrize("year_out_of_range", error_cases)
def test_coords_raises_error(year_out_of_range):
    """Tests that `get_coords` raises a `EphemerisRangeError` when the year is out of range.
    Verifies that the error message matches the expected text.
    """
    from skyfield.errors import EphemerisRangeError
    with pytest.raises(EphemerisRangeError, match=range_error_message):
        get_coords(year_out_of_range)


@pytest.mark.parametrize("year_out_of_range", error_cases)
def test_seasons_error(year_out_of_range):
    """Tests that `get_seasons` raises an `EphemerisRangeError` when the year is out of range.
    Verifies that the error message matches the expected text.
    """
    from skyfield.errors import EphemerisRangeError
    with pytest.raises(EphemerisRangeError, match=range_error_message):
        get_seasons(year_out_of_range)
