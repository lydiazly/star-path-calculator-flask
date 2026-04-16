# -*- coding: utf-8 -*-
# tests/test_time_utils.py
import pytest
from core.data_loader import timescale
from utils.time_utils import (
    get_tzid_by_tzfpy,
    get_standard_offset_by_id,
    ut1_to_standard_time,
    ut1_to_local_mean_time,
    gregorian_to_julian,
    julian_to_gregorian,
)


@pytest.mark.parametrize(
    "lat, lng, tz_expected",
    [
        (0, 0, 'Etc/GMT'),  # GMT
        (40, -180, 'Etc/GMT+12'),  # Etc/GMT±12
        (40, 180, 'Etc/GMT-12'),  # Etc/GMT±12
        (40, -179.9999, 'Etc/GMT+12'),  # Etc/GMT+12
        (47.650499, -122.350070, 'America/Los_Angeles'),  # Los Angeles
        (49.3, -123.1, 'America/Vancouver'),  # Vancouver
        (43.839319, 87.526148, 'Asia/Shanghai'),  # Ürümqi
        (47.8, 88.1, 'Asia/Shanghai'),  # Altay
        (22.598127, 120.347287, "Asia/Taipei"),  # Taipei
        (53.3, -110.0, 'America/Edmonton'),  # Lloydminster, Alberta
        (-33.8698439, 151.2082848, 'Australia/Sydney'),  # Sydney
        # (45.036933, 12.826174, 'Asia/Riyadh'),  # 'Europe/Rome' (incorrect) Aden International Airport
        (91, 0, ''),  # Invalid
        (0, 181, ''),  # Invalid
    ],
)
def test_timezone(lat, lng, tz_expected):
    """Tests the time zone ID finder."""
    assert get_tzid_by_tzfpy(lat, lng) == tz_expected


@pytest.mark.parametrize(
    "tz_id, offset_in_hours_expected, tzname_expected",
    [
        ('Europe/London', '0.0', 'GMT'),
        ('America/Vancouver', '-8.0', 'PST'),
        ('Asia/Shanghai', '8.0', 'CST'),
        ('Asia/Urumqi', '6.0', '+06'),
        ('America/New_York', '-5.0', 'EST'),
        ('Australia/Sydney', '10.0', 'AEST'),
    ],
)
def test_standard_offset(tz_id, offset_in_hours_expected, tzname_expected):
    """Tests getting the Standard Time offset."""
    offset_in_minutes, tz_name = get_standard_offset_by_id(tz_id)
    assert f'{offset_in_minutes / 60:.1f}' == offset_in_hours_expected
    assert tz_name == tzname_expected


test_times = [
    ((2000, 1, 1, 12, 0, 0), -8, -120, (2000, 1, 1, 4, 0, 0)),
    ((2000, 1, 1, 12, 0, 0), -7.5, -112.5, (2000, 1, 1, 4, 30, 0)),
    ((2000, 1, 1, 12, 0, 0), 5.5, 82.5, (2000, 1, 1, 17, 30, 0)),
]


@pytest.mark.parametrize("t_ut1, offset_in_hours, _, t_standard_expected", test_times)
def test_ut1_to_standard_time(t_ut1, offset_in_hours, _, t_standard_expected):
    """Tests UT1 to standard time conversion."""
    t = ut1_to_standard_time(t_ut1, offset_in_hours * 60)
    assert (
        tuple(map(int, timescale.ut1(*t[:5], round(t[5]) + 0.1).ut1_calendar()))
        == t_standard_expected
    )


@pytest.mark.parametrize("t_ut1, _, lng, t_standard_expected", test_times)
def test_ut1_to_local_mean_time(t_ut1, _, lng, t_standard_expected):
    """Tests UT1 to LMT conversion."""
    t = ut1_to_local_mean_time(t_ut1, lng)
    assert (
        tuple(map(int, timescale.ut1(*t[:5], round(t[5]) + 0.1).ut1_calendar()))
        == t_standard_expected
    )


# https://en.wikipedia.org/wiki/Conversion_between_Julian_and_Gregorian_calendars
test_dates = [
    ((-500, 2, 28), (-500, 3, 5)),
    ((1582, 10, 15), (1582, 10, 5)),
    ((2100, 3, 14), (2100, 2, 29)),
]


@pytest.mark.parametrize("date_g, date_j", test_dates)
def test_gregorian_to_julian(date_g, date_j):
    """Tests Gregorian to Julian conversion."""
    assert gregorian_to_julian(date_g)[:3] == date_j


@pytest.mark.parametrize("date_g, date_j", test_dates)
def test_julian_to_gregorian(date_j, date_g):
    """Tests Julian to Gregorian conversion."""
    assert julian_to_gregorian(date_j)[:3] == date_g
