# -*- coding: utf-8 -*-
# tests/test_hip.py
import pytest
import numpy as np
import os
import core.data_loader as dl
from utils.star_utils import hip_to_name


# https://www.cosmos.esa.int/web/hipparcos/catalogues
@pytest.mark.parametrize(
    "hip_valid, radec_expected",
    [
        (87937, "269.454, 4.668"),
        ( 8102, "26.021, -15.940"),
        (32349, "101.289, -16.713"),
        (71683, "219.920, -60.835"),
        (70890, "217.449, -62.681"),
    ]
)
def test_hip_valid(hip_valid, radec_expected):
    """Tests valid HIP entries."""
    s = dl.hip_df.loc[hip_valid]
    assert f"{s['ra_degrees']:.3f}, {s['dec_degrees']:.3f}" == radec_expected


def parse_hip_from_file(filename):
    """Parses the file containing invalid HIP numbers.

    To generate the file, in the root dir:
    $ python -c "from utils.data_utils import hip_validation; hip_validation()" > tests/hip_invalid.txt
    """
    hip_missing, hip_invalid = [], []
    with open(filename, "r") as file:
        for line in file:
            hip = line.split(":")[0].strip()
            if hip.startswith("-"):  # invalid (no radec)
                hip_number = int(hip.split("=")[1].strip())
                hip_invalid.append(hip_number)
            elif hip.startswith("*"):  # missing
                hip_number = int(hip.split("=")[1].strip())
                hip_missing.append(hip_number)
    return hip_invalid, hip_missing


# Read HIP numbers from the file
hip_invalid, hip_missing = parse_hip_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hip_invalid.txt"))

@pytest.mark.parametrize("hip_invalid", hip_invalid)
def test_hip_invalid(hip_invalid):
    """Tests HIP entries where the ra/dec is NaN."""
    ra = dl.hip_df.loc[hip_invalid, 'ra_degrees']
    assert np.isnan(ra), f"Expected NaN but got {ra}."


@pytest.mark.parametrize("hip_missing", hip_missing)
def test_hip_no_entry(hip_missing):
    """Tests non-existent HIP entries."""
    with pytest.raises(KeyError, match=f"{hip_missing}"):
        dl.hip_df.loc[hip_missing]


@pytest.mark.parametrize(
    "hip, name_expected",
    [
        (91262, 'alf_Lyr/3_Lyr/Vega'),
        (11767, 'alf_UMi/1_UMi/Polaris'),
        (82080, 'eps_UMi/22_UMi'),
        (102098, 'alf_Cyg/50_Cyg/Deneb'),
        (0, ''),
        (123, ''),
    ]
)
def test_hip_to_name(hip, name_expected):
    """Tests finding the name of a given HIP."""
    assert hip_to_name(hip) == name_expected
