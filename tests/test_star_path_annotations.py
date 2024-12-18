# -*- coding: utf-8 -*-
# tests/test_star_path_annotations.py
import os
import json
import pytest
from core.star_path import StarObject


# Load test cases from JSON file
def load_test_cases():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_cases.json"), "r") as f:
        return json.load(f)


@pytest.mark.parametrize("test_case", load_test_cases())
def test_annotations(test_case):
    s = StarObject(**test_case['input'])
    res = s.generate_result()['annotations']
    del s
    res = json.loads(json.dumps(res))  # make sure all tuples converted to lists
    dict1 = {p['name']: p for p in [p for p in res if p['is_displayed']]}
    dict2 = {p['name']: p for p in test_case['expected']}
    assert dict1 == dict2
