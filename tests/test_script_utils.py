# -*- coding: utf-8 -*-
# tests/test_script_utils.py
import pytest
from utils.script_utils import format_datetime_iso, decimal_to_hms


@pytest.mark.parametrize(
    "datetime_tuple, datetime_str_expected",
    [
        ((2000,),                   ['+2000-01-01', '12:00:00']),
        ((20000, 12, 31),          ['+20000-12-31', '12:00:00']),
        ((100, 2, 15, 1, 1, 1),     ['+0100-02-15', '01:01:01']),
        ((0, 1, 1, 0, 0, 0.12345),  ['+0000-01-01', '00:00:00.123']),
        ((-3000, 1, 1, 0, 0, 0.1),  ['-3000-01-01', '00:00:00.100']),
        ((-30000,),                ['-30000-01-01', '12:00:00']),
    ]
)
def test_format_datetime_iso(datetime_tuple, datetime_str_expected):
    assert format_datetime_iso(*datetime_tuple) == datetime_str_expected


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
    assert decimal_to_hms(decimal_hours) == hms_expected
