# -*- coding: utf-8 -*-
# tests/test_time_utils.py
import pytest
from skyfield.api import load
from utils.time_utils import find_timezone, get_standard_offset_by_id, ut1_to_standard_time, ut1_to_local_mean_time, gregorian_to_julian, julian_to_gregorian


tisca = load.timescale()


@pytest.mark.parametrize(
    "lat, lng, tz_expected",
    [
        (49.3, -123.1, 'America/Vancouver'),  # Vancouver
        (43.8, 87.6,   'Asia/Shanghai'),  # Ürümqi
        (47.8, 88.1,   'Asia/Shanghai'),  # Altay
        (53.3, -110.0, 'America/Edmonton'),  # Lloydminster, Alberta
        (91, 0, ''),  # Invalid
        (0, 181, ''),  # Invalid
    ]
)
def test_timezone(lat, lng, tz_expected):
    """Tests the time zone identifier finder."""
    assert find_timezone(lat, lng) == tz_expected


@pytest.mark.parametrize(
    "tz_id, offset_in_hours_expected",
    [
        ('America/Vancouver', '-8.0'),
        ('Asia/Shanghai',      '8.0'),
        ('Asia/Urumqi',        '6.0'),
    ]
)
def test_standard_offset(tz_id, offset_in_hours_expected):
    """Tests getting the UT1 offset in hours."""
    assert f'{get_standard_offset_by_id(tz_id)/60:.1f}' == offset_in_hours_expected

test_times = [
    ((2000, 1, 1, 12, 0, 0), -8,   -120,   (2000, 1, 1, 4, 0, 0)),
    ((2000, 1, 1, 12, 0, 0), -7.5, -112.5, (2000, 1, 1, 4, 30, 0)),
    ((2000, 1, 1, 12, 0, 0),  5.5,   82.5, (2000, 1, 1, 17, 30, 0)),
]

@pytest.mark.parametrize("t_ut1, offset_in_hours, _, t_standard_expected", test_times)
def test_ut1_to_standard_time(t_ut1, offset_in_hours, _, t_standard_expected):
    """Tests UT1 to standard time conversion."""
    t = ut1_to_standard_time(t_ut1, offset_in_hours * 60)
    assert tuple(map(int, tisca.ut1(*t[:5], round(t[5]) + 0.1).ut1_calendar())) == t_standard_expected


@pytest.mark.parametrize("t_ut1, _, lng, t_standard_expected", test_times)
def test_ut1_to_local_mean_time(t_ut1, _, lng, t_standard_expected):
    """Tests UT1 to LMT conversion."""
    t = ut1_to_local_mean_time(t_ut1, lng)
    assert tuple(map(int, tisca.ut1(*t[:5], round(t[5]) + 0.1).ut1_calendar())) == t_standard_expected


# https://en.wikipedia.org/wiki/Conversion_between_Julian_and_Gregorian_calendars
test_dates = [
    ((-500, 2, 28),  (-500, 3, 5)),
    ((1582, 10, 15), (1582, 10, 5)),
    ((2100, 3, 14),  (2100, 2, 29)),
]

@pytest.mark.parametrize("date_g, date_j", test_dates)
def test_gregorian_to_julian(date_g, date_j):
    """Tests Gregorian to Julian conversion."""
    assert gregorian_to_julian(date_g)[:3] == date_j


@pytest.mark.parametrize("date_g, date_j", test_dates)
def test_julian_to_gregorian(date_j, date_g):
    """Tests Julian to Gregorian conversion."""
    assert julian_to_gregorian(date_j)[:3] == date_g
