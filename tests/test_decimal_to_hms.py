# -*- coding: utf-8 -*-
# tests/test_decimal_to_hms.py
import pytest
from utils.script_utils import decimal_to_hms

@pytest.mark.parametrize("decimal_values, hms_expected", [
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
])

def test_decimal_to_hms(decimal_values, hms_expected):
    assert decimal_to_hms(decimal_values) == hms_expected
