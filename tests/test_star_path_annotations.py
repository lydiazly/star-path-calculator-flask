# -*- coding: utf-8 -*-
# tests/test_star_path_annotations.py
from importlib.metadata import version, PackageNotFoundError
import json
import numpy
from packaging.version import Version
from pathlib import Path
import platform
import pytest
import skyfield

from starpathcalculator.core.star_path import StarObject, get_diagram
from helpers import assert_iterable_equal

# Skip every test in this module
# pytestmark = pytest.mark.skip(reason="Cases are outdated, do not run")

# rel_tol = 1e-9  # default in math.isclose()
rel_tol = 3e-9  # for compatibility
abs_tol = 1e-5
abs_tol_thred = 5e-5

try:
    __version__ = version('star-path-calculator')
except PackageNotFoundError:
    __version__ = ''

# if Version(numpy.__version__) < Version('2.0.0'):
#     rel_tol = 5e-9 if Version(skyfield.__version__) <= Version('1.49') else 5e-8
if Version(skyfield.__version__) >= Version('1.54'):
    rel_tol = 2e-7

print("\n=== Annotations ===")
print(f"Package version: {__version__}")
print(f"python: {platform.python_version()}")
print(f"numpy: {numpy.__version__}, skyfield: {skyfield.__version__}")
print(f"Relative tolerance: {rel_tol:.0e}")
print(f"Absolute tolerance for value <= {abs_tol_thred:.0e}: {abs_tol:.0e}")

if Version(skyfield.__version__) <= Version('1.49'):
    cases_filename = 'cases/anno_skyfield1.49_docker.json'
    print("Test cases (docker): 0.1.0, python 3.12.3, numpy 2.2.3, skyfield 1.49")
else:
    # cases_filename = 'cases/anno_skyfield1.49_docker.json'
    # print("Test cases (docker): python 3.12.3, numpy 2.2.3, skyfield 1.49")
    # cases_filename = 'cases/anno_skyfield1.51_docker.json'
    # print("Test cases (docker): 0.1.0, python 3.12.3, numpy 2.2.3, skyfield 1.51")
    cases_filename = 'cases/anno_skyfield1.54_0.1.1_docker.json'
    print("Test cases (docker): 0.1.1, python 3.12.3, numpy 2.4.4, skyfield 1.54")

print(f"Loading '{cases_filename}'")

with open(Path(__file__).parent.parent / cases_filename) as f:
    CASES = json.load(f)


@pytest.mark.parametrize("case", CASES, ids=[c['id'] for c in CASES])
def test_annotations(case):
    """Tests the annotations of the generated diagram.
    Compares two floats with a relative tolerance `rel_tol`.
    """

    res = get_diagram(**case['input'])['annotations']
    # make sure all tuples converted to lists
    res = json.loads(json.dumps(res))
    d1 = {p['name']: p for p in [p for p in res if p['is_displayed']]}
    d2 = {p['name']: p for p in case['expected']}

    assert_iterable_equal(
        d1, d2, rel_tol=rel_tol, abs_tol=abs_tol, abs_tol_thred=abs_tol_thred
    )


test_date_coords_dict = {'year': -2000, 'month': 3, 'day': 1, 'lat': 40.19, 'lng': 116.41, 'tz_id': 'Asia/Shanghai'}  # fmt: skip

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
