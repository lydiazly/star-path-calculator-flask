# -*- coding: utf-8 -*-
# tests/test_seasons.py
import json
import numpy
from packaging.version import Version
from pathlib import Path
import platform
import pytest
import skyfield
from core.seasons import get_coords, get_seasons
from .helpers import assert_dicts_equal

# Docker results (same as local tests)
cases_filename = 'cases/cases_seasons_skyfield1.49_docker.json'

rel_tol = 1e-9  # default in math.isclose()
if Version(skyfield.__version__) > Version('1.49'):
    rel_tol = 6e-4

print("\n=== Seasons ===")
print(f"python: {platform.python_version()}")
print(f"numpy: {numpy.__version__}, skyfield: {skyfield.__version__}")
print(f"Relative tolerance: {rel_tol:.0e}")
print("Test cases (docker): python 3.12.3, numpy 2.2.3, skyfield 1.49")
print(f"Loading '{cases_filename}'")


with open(Path(__file__).parent.parent / cases_filename) as f:
    CASES = json.load(f)


@pytest.mark.parametrize("case", CASES, ids=[c['id'] for c in CASES])
def test_coords(case):
    """Tests calculating the times and coordinates of equinoxes and solstices.
    Compares two floats with a relative tolerance `rel_tol`.
    """
    res = get_coords(case['input'])
    assert_dicts_equal(res, case['expected'], rel_tol=rel_tol)


@pytest.mark.parametrize("case", CASES, ids=[c['id'] for c in CASES])
def test_seasons(case):
    """Tests calculating the times of equinoxes and solstices.
    Times should be the same as the results of `get_coords(year)`.
    Compares two floats with a relative tolerance `rel_tol`.
    """
    res = get_seasons(case['input'])
    expected = {
        k: case['expected'][k]
        for k in ['vernal_time', 'summer_time', 'autumnal_time', 'winter_time']
    }
    assert_dicts_equal(res, expected, rel_tol=rel_tol)


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
