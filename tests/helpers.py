# -*- coding: utf-8 -*-
# tests/helpers.py
import pytest


def assert_dicts_equal(d1: dict, d2: dict, sig_digits: int = 16):
    """Asserts that two dictionaries are equal with tolerance for floats.
    Floats are compared based on their string representation with
    the specified number of significant digits.
    """
    differences = dict_diff(d1, d2, sig_digits=sig_digits)
    if differences:
        formatted_diff = ["", "--- dict1 (actual)", "+++ dict2 (expected)", ""]
        formatted_diff.extend(differences)
        pytest.fail("\n".join(formatted_diff))


def dict_diff(d1: dict, d2: dict, path="", sig_digits: int = 16):
    """Recursively finds differences between two nested dictionaries.
    Compares two floats with a tolerance based on significant digits
    """
    differences = []

    # Keys in d1 but not in d2
    for k in sorted(set(d1) - set(d2)):
        full_path = f"{path}.{k}" if path else k
        differences.append(f"-{full_path}: {repr(d1[k])}")

    # Keys in d2 but not in d1
    for k in sorted(set(d2) - set(d1)):
        full_path = f"{path}.{k}" if path else k
        differences.append(f"+{full_path}: {repr(d2[k])}")

    # Keys in both but values differ
    for k in sorted(set(d1) & set(d2)):
        full_path = f"{path}.{k}" if path else k
        if d1[k] != d2[k]:
            if sig_digits < 16 and isinstance(d1[k], float) and isinstance(d2[k], float):
                if f'{d1[k]:.{sig_digits}g}' == f'{d2[k]:.{sig_digits}g}':
                    print(f"\n*{full_path}: {d1[k]:.{sig_digits}g} (match with tolerance: {sig_digits} sig digits)")
                else:
                    differences.append(f"-{full_path}: {d1[k]:.{sig_digits}g}")
                    differences.append(f"+{full_path}: {d2[k]:.{sig_digits}g} (tolerance: {sig_digits} sig digits)")
            else:
                if isinstance(d1[k], dict) and isinstance(d2[k], dict):
                    # Recursively handle nested dictionaries
                    nested_diff = dict_diff(d1[k], d2[k], full_path, sig_digits)
                    differences.extend(nested_diff)
                else:
                    differences.append(f"-{full_path}: {repr(d1[k])}")
                    differences.append(f"+{full_path}: {repr(d2[k])}")

    return differences
