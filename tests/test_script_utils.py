# -*- coding: utf-8 -*-
# tests/test_script_utils.py
import pytest
from utils.script_utils import format_datetime, format_datetime_iso, validate_datetime, validate_year, decimal_to_hms, format_timezone


@pytest.mark.parametrize(
    "datetime_dict, datetime_str_expected",
    [
        ({'year': 2000, 'year_only': True}, '2000 CE'),
        ({'year': 0, 'year_only': True}, '1 BCE'),
        ({'year': -3000, 'year_only': True}, '3001 BCE'),
        ({'year': -30000, 'year_only': True}, '30001 BCE'),
        ({'year': 2024, 'month': 9, 'day': 2, 'hour': 23, 'minute': 59, 'second': 59.999}, ('2 Sep 2024 CE', '23:59:59.999')),
        ({'year': 0, 'month': 12, 'day': 31, 'hour': 23, 'minute': 59, 'second': 59.9999}, ('31 Dec 1 BCE', '23:59:60.000')),
        ({'year': -500, 'month': 1, 'day': 3, 'month_first': True}, ('Jan 3, 501 BCE', '12:00:00')),
        ({'year': -500, 'month': 1, 'day': 3, 'month_first': True, 'abbr': False}, ('January 3, 501 BCE', '12:00:00')),
        ({'year': -500, 'month': 1, 'day': 3, 'abbr': False}, ('3 January 501 BCE', '12:00:00')),
    ]
)
def test_format_datetime(datetime_dict, datetime_str_expected):
    """Tests formatting the datetime in ISO 8601."""
    assert format_datetime(**datetime_dict) == datetime_str_expected


@pytest.mark.parametrize("month_out_of_range", [(2000, -1), (2000, 0), (2000, 13)])
def test_format_datetime_error(month_out_of_range):
    """
    Tests that `format_datetime` raises an `ValueError` when the month is out of range.
    Verifies that the error message matches the expected text.
    """
    with pytest.raises(ValueError, match=r"^Month index out of range\.$"):
        format_datetime(*month_out_of_range)


@pytest.mark.parametrize(
    "datetime_tuple, datetime_str_expected",
    [
        ((2000,),                   ('+2000-01-01', '12:00:00')),
        ((20000, 12, 31),          ('+20000-12-31', '12:00:00')),
        ((100, 2, 15, 1, 1, 1),     ('+0100-02-15', '01:01:01')),
        ((0, 1, 1, 0, 0, 0.12345),  ('+0000-01-01', '00:00:00.123')),
        ((-3000, 1, 1, 0, 0, 0.1),  ('-3000-01-01', '00:00:00.100')),
        ((-30000,),                ('-30000-01-01', '12:00:00')),
    ]
)
def test_format_datetime_iso(datetime_tuple, datetime_str_expected):
    """Tests formatting the datetime in ISO 8601."""
    assert format_datetime_iso(*datetime_tuple) == datetime_str_expected


range_error_message = r"^Out of the ephemeris date range: -3000-01-29/\+3000-05-06$"

@pytest.mark.parametrize(
    "invalid_datetime, message_expected",
    [
        ((-3001, 12, 31), range_error_message),
        ((-3000, 1, 28),  range_error_message),
        ((3001, 1, 1),    range_error_message),
        ((3000, 6, 1),    range_error_message),
        ((3000, 5, 7),    range_error_message),
        ((-3001, 2, 29),  r"^Invalid date: \[year, month, day\] = \[-3001, 2, 29\]$"),
        ((-3001, 2, 28, 0, 0, 60), r"^Invalid time: 0:0:60$"),
    ]
)
def test_validate_datetime(invalid_datetime, message_expected):
    """Tests the datetime validation and verifies the error message."""
    with pytest.raises(ValueError, match=message_expected):
        validate_datetime(*invalid_datetime)


@pytest.mark.parametrize("invalid_year", [-3000, 3000])
def test_validate_year(invalid_year):
    """Tests the year validation and verifies the error message."""
    with pytest.raises(ValueError, match=r"^Out of the year range: -2999/\+2999$"):
        validate_year(invalid_year)


@pytest.mark.parametrize(
    "decimal_hours, hms_expected",
    [
        (0,        {'sign':  1, 'hours':  0, 'minutes':  0, 'seconds':  0}),
        (-0,       {'sign':  1, 'hours':  0, 'minutes':  0, 'seconds':  0}),
        (-0.5,     {'sign': -1, 'hours':  0, 'minutes': 30, 'seconds':  0}),
        (1.5,      {'sign':  1, 'hours':  1, 'minutes': 30, 'seconds':  0}),
        (-1.5,     {'sign': -1, 'hours':  1, 'minutes': 30, 'seconds':  0}),
        (2.75,     {'sign':  1, 'hours':  2, 'minutes': 45, 'seconds':  0}),
        (1.999,    {'sign':  1, 'hours':  1, 'minutes': 59, 'seconds': 56}),
        (1.9999,   {'sign':  1, 'hours':  2, 'minutes':  0, 'seconds':  0}),
        (1.99999,  {'sign':  1, 'hours':  2, 'minutes':  0, 'seconds':  0}),
        (10.5,     {'sign':  1, 'hours': 10, 'minutes': 30, 'seconds':  0}),
        (-10.75,   {'sign': -1, 'hours': 10, 'minutes': 45, 'seconds':  0}),
    ]
)
def test_decimal_to_hms(decimal_hours, hms_expected):
    """Tests the decimal hours to HMS conversion."""
    assert decimal_to_hms(decimal_hours) == hms_expected


@pytest.mark.parametrize(
    "offset_in_hours, tz_str",
    [
        (-8, "-08:00"),
        (8, "+08:00"),
        (0, "+00:00"),
    ]
)
def test_format_timezone(offset_in_hours, tz_str):
    """Tests formatting the UT1 offset in hours."""
    assert format_timezone(offset_in_hours) == tz_str
