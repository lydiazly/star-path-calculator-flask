#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.script_utils import decimal_to_hms

def test_decimal_to_hms():
    test_cases = [
        (0, {'sign': 1, 'hours': 0, 'minutes': 0, 'seconds': 0}),
        (1.5, {'sign': 1, 'hours': 1, 'minutes': 30, 'seconds': 0}),
        (-1.5, {'sign': -1, 'hours': 1, 'minutes': 30, 'seconds': 0}),
        (2.75, {'sign': 1, 'hours': 2, 'minutes': 45, 'seconds': 0}),
        (1.999, {'sign': 1, 'hours': 1, 'minutes': 59, 'seconds': 56}),
        (1.9999, {'sign': 1, 'hours': 2, 'minutes': 0, 'seconds': 0}),
        (1.99999, {'sign': 1, 'hours': 2, 'minutes': 0, 'seconds': 0}),
        (10.5, {'sign': 1, 'hours': 10, 'minutes': 30, 'seconds': 0}),
        (-10.75, {'sign': -1, 'hours': 10, 'minutes': 45, 'seconds': 0}),
    ]

    for i, (input_val, expected) in enumerate(test_cases):
        result = decimal_to_hms(input_val)
        assert result == expected, f"Test case {i+1} failed: {result} != {expected}"
    print("All test cases passed!")

test_decimal_to_hms()