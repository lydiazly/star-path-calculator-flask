# -*- coding: utf-8 -*-
# tests/test_time_utils.py
import pytest
from utils.time_utils import find_timezone, get_standard_offset_by_id, gregorian_to_julian, julian_to_gregorian


@pytest.mark.parametrize(
    "lat, lng, tz_expected",
    [
        (49.3, -123.1, 'America/Vancouver'),  # Vancouver
        (43.8, 87.6,   'Asia/Shanghai'),  # Ürümqi
        (47.8, 88.1,   'Asia/Shanghai'),  # Altay
        (53.3, -110.0, 'America/Edmonton'),  # Lloydminster, Alberta
    ]
)
def test_timezone(lat, lng, tz_expected):
    assert find_timezone(lat, lng) == tz_expected


@pytest.mark.parametrize(
    "tz_id, offset_hours_expected",
    [
        ('America/Vancouver', '-8.0'),
        ('Asia/Shanghai',      '8.0'),
        ('Asia/Urumqi',        '6.0'),
    ]
)
def test_standard_offset(tz_id, offset_hours_expected):
    assert f'{get_standard_offset_by_id(tz_id)/60:.1f}' == offset_hours_expected


# https://en.wikipedia.org/wiki/Conversion_between_Julian_and_Gregorian_calendars
test_dates = [
    ((-500, 2, 28),  (-500, 3, 5)),
    ((1582, 10, 15), (1582, 10, 5)),
    ((2100, 3, 14),  (2100, 2, 29)),
]


@pytest.mark.parametrize("date_g, date_j", test_dates)
def test_gregorian_to_julian(date_g, date_j):
    assert gregorian_to_julian(date_g)[:3] == date_j


@pytest.mark.parametrize("date_g, date_j", test_dates)
def test_julian_to_gregorian(date_j, date_g):
    assert julian_to_gregorian(date_j)[:3] == date_g
