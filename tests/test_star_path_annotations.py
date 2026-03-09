# -*- coding: utf-8 -*-
# tests/test_star_path_annotations.py
import platform
import os
import json
import pytest
from packaging.version import Version
import numpy
import skyfield
from core.star_path import StarObject, get_diagram
from .helpers import assert_dicts_equal


# rel_tol = 1e-9  # default in math.isclose()
rel_tol = 2e-9  # for compatibility when running in the server
# if Version(numpy.__version__) < Version('2.0.0'):
#     rel_tol = 5e-9 if Version(skyfield.__version__) <= Version('1.49') else 5e-8

print("\n=== Annotations ===")
print(f"python: {platform.python_version()}")
print(f"numpy: {numpy.__version__}, skyfield: {skyfield.__version__}")
print(f"Relative tolerance: {rel_tol:.0e}")

if Version(skyfield.__version__) <= Version('1.49'):
    example_cases_filename = 'example_cases_skyfield1.49.json'
    print("Test cases: numpy 2.2.3, skyfield 1.49")
else:
    # example_cases_filename = 'example_cases_skyfield1.49.json'
    # print("Test cases: numpy 2.2.3, skyfield 1.49")
    example_cases_filename = 'example_cases_skyfield1.51.json'
    print("Test cases: numpy 2.2.3, skyfield 1.51")


def load_test_cases():
    """Loads test cases from a JSON file."""
    print(f"Loading 'tests/{example_cases_filename}'")
    full_filename = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), example_cases_filename
    )
    with open(full_filename, "r") as f:
        return json.load(f)


@pytest.mark.parametrize("test_case", load_test_cases())
def test_annotations(test_case):
    """Tests the annotations of the generated diagram.
    Compares two floats with a relative tolerance `rel_tol`.
    """

    res = get_diagram(**test_case['input'])['annotations']
    # make sure all tuples converted to lists
    res = json.loads(json.dumps(res))
    d1 = {p['name']: p for p in [p for p in res if p['is_displayed']]}
    d2 = {p['name']: p for p in test_case['expected']}

    assert_dicts_equal(d1, d2, rel_tol=rel_tol)


test_date_coords_dict = {"year": -2000, "month": 3, "day": 1, "lat": 40.19, "lng": 116.41, "tz_id": "Asia/Shanghai"}

invalid_cases = [
    (test_date_coords_dict, r"^Invalid celestial object\.$"),
    (
        {**test_date_coords_dict, 'name': 'Not_a_planet'},
        r"^Invalid planet name: not_a_planet$",
    ),
    (
        {**test_date_coords_dict, 'hip': 118323},
        r"^The Hipparcos Catalogue number must be in the range \[1, 118322\]\.$",
    ),
    (
        {**test_date_coords_dict, 'hip': 0},
        r"^The Hipparcos Catalogue number must be in the range \[1, 118322\]\.$",
    ),
    (
        {**test_date_coords_dict, 'hip': 421},
        r"^WARNING: No RA/Dec data available for this star in the Hipparcos Catalogue\.$",
    ),
    (
        {**test_date_coords_dict, 'hip': 672},
        r"^WARNING: Entry not found in the Hipparcos Catalogue\.$",
    ),
]


@pytest.mark.parametrize("invalid_input, message_expected", invalid_cases)
def test_invalid_star(invalid_input, message_expected):
    """Tests the error raised when instantiating a `StarObject` and verifies the error message."""
    with pytest.raises(ValueError, match=message_expected):
        s = StarObject(**invalid_input)
        del s


@pytest.mark.parametrize(
    "input",
    [
        {**test_date_coords_dict, 'hip': 30438},
        {**test_date_coords_dict, 'radec': (0, -45)},
    ],
)
def test_never_rises_cases(input):
    """Tests the error raised when a star never rises and verifies the error message."""
    with pytest.raises(
        ValueError,
        match=r"^WARNING: This star never rises at this location on this date\.$",
    ):
        s = StarObject(**input)
        _ = s.generate_result()['annotations']
        del s
