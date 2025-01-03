# -*- coding: utf-8 -*-
# tests/test_hip.py
import pytest
import numpy as np
import os
import core.data_loader as dl


# https://www.cosmos.esa.int/web/hipparcos/catalogues
@pytest.mark.parametrize("hip_valid, radec_expected", [
    (87937, "269.454, 4.668"),
    ( 8102, "26.021, -15.940"),
    (32349, "101.289, -16.713"),
    (71683, "219.920, -60.835"),
    (70890, "217.449, -62.681"),
])

def test_hip_valid(hip_valid, radec_expected):
    """Tests valid HIP entries."""
    s = dl.hip_df.loc[hip_valid]
    assert f"{s['ra_degrees']:.3f}, {s['dec_degrees']:.3f}" == radec_expected


def parse_hip_from_file(filename):
    """
    Parses the file containing invalid HIP numbers.
    To generate the file, in the root dir:
    $ python -c "from utils.data_utils import hip_validation; hip_validation()" > tests/hip_invalid.txt
    """
    hip_no_entry, hip_invalid = [], []
    with open(filename, "r") as file:
        for line in file:
            hip = line.split(":")[0].strip()
            if hip.startswith("-"):  # invalid (no radec)
                hip_number = int(hip.split("=")[1].strip())
                hip_invalid.append(hip_number)
            elif hip.startswith("*"):  # no entry
                hip_number = int(hip.split("=")[1].strip())
                hip_no_entry.append(hip_number)
    return hip_invalid, hip_no_entry


# Read HIP numbers from the file
hip_invalid, hip_no_entry = parse_hip_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hip_invalid.txt"))


@pytest.mark.parametrize("hip_invalid", hip_invalid)
def test_hip_invalid(hip_invalid):
    """Tests HIP entries where the ra/dec is NaN."""
    ra = dl.hip_df.loc[hip_invalid, 'ra_degrees']
    assert np.isnan(ra), f"Expected NaN but got {ra}."


@pytest.mark.parametrize("hip_no_entry", hip_no_entry)
def test_hip_no_entry(hip_no_entry):
    """Tests non-existent HIP entries."""
    with pytest.raises(KeyError, match=f"{hip_no_entry}"):
        dl.hip_df.loc[hip_no_entry]
