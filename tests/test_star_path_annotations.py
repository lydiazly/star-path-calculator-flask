# -*- coding: utf-8 -*-
# tests/test_star_path_annotations.py
import os
import json
import pytest
from packaging.version import Version
import numpy as np
from core.star_path import StarObject, get_diagram
from .helpers import assert_dicts_equal


def load_test_cases():
    """Loads test cases from a JSON file."""
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_cases.json"), "r") as f:
        return json.load(f)


@pytest.mark.parametrize("test_case", load_test_cases())
def test_annotations(test_case):
    """Tests the annotations of the generated diagram."""
    res = get_diagram(**test_case['input'])['annotations']
    res = json.loads(json.dumps(res))  # make sure all tuples converted to lists
    d1 = {p['name']: p for p in [p for p in res if p['is_displayed']]}
    d2 = {p['name']: p for p in test_case['expected']}
    assert_dicts_equal(d1, d2, sig_digits=(8 if Version(np.__version__) < Version('2.0.0') else 16))


test_date_coords_dict = {"year": -2000, "month": 3, "day": 1, "lat": 40.19, "lng": 116.41, "tz_id": "Asia/Shanghai"}

invalid_cases = [
    (test_date_coords_dict, r"^Invalid celestial object\.$"),
    ({**test_date_coords_dict, 'name': 'Not_a_planet'}, r"^Invalid planet name: not_a_planet$"),
    ({**test_date_coords_dict, 'hip': 118323}, r"^The Hipparcos Catalogue number must be in the range \[1, 118322\]\.$"),
    ({**test_date_coords_dict, 'hip': 0},      r"^The Hipparcos Catalogue number must be in the range \[1, 118322\]\.$"),
    ({**test_date_coords_dict, 'hip': 421}, r"^WARNING: No RA/Dec data available for this star in the Hipparcos Catalogue\.$"),
    ({**test_date_coords_dict, 'hip': 672}, r"^WARNING: Entry not found in the Hipparcos Catalogue\.$"),
]

@pytest.mark.parametrize("invalid_input, message_expected", invalid_cases)
def test_invalid_star(invalid_input, message_expected):
    """Tests the error raised when instantiating a `StarObject` and verifies the error message."""
    with pytest.raises(ValueError, match=message_expected):
        s = StarObject(**invalid_input)
        del s


@pytest.mark.parametrize("input",
    [
        {**test_date_coords_dict, 'hip': 30438},
        {**test_date_coords_dict, 'radec': (0, -45)},
    ]
)
def test_never_rises_cases(input):
    """Tests the error raised when a star never rises and verifies the error message."""
    with pytest.raises(ValueError, match=r"^WARNING: This star never rises at this location on this date\.$"):
        s = StarObject(**input)
        _ = s.generate_result()['annotations']
        del s
