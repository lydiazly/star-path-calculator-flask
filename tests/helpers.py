# -*- coding: utf-8 -*-
# tests/helpers.py
import math
import pytest


def assert_dicts_equal(d1: dict, d2: dict, rel_tol=1e-9):
    """Asserts that two dictionaries are equal with tolerance for floats.
    Floats are compared based on their string representation with
    the specified number of significant digits.
    """
    differences = dict_diff(d1, d2, rel_tol=rel_tol)
    if differences:
        formatted_diff = ["", "--- dict1 (actual)", "+++ dict2 (expected)", ""]
        formatted_diff.extend(differences)
        pytest.fail("\n".join(formatted_diff))


def dict_diff(d1, d2, path="", rel_tol=1e-9):
    """Recursively finds differences between two nested lists/tuples/dicts.
    Compares two floats using `math.isclose(a, b, rel_tol)` with a
    relative tolerance `rel_tol` that:
    if `abs(a - b) < rel_tol * max(abs(a), abs(b))`,
    then `a` and `b` are considered "close" to each other.
    """
    differences = []

    # Id d1 is a list/tuple
    if isinstance(d1, list) or isinstance(d1, tuple):
        # If d2 is not a list/tuple, mark and return
        if not (isinstance(d2, list) or isinstance(d2, tuple)):
            differences.append(f"-{path}: {repr(d1)}")
            differences.append(f"+{path}: {repr(d2)}")
            return differences

        # Otherwise, check each element
        for i in range(len(d1)):
            full_path = f"{path}[{i}]" if path else i
            if d1[i] != d2[i]:
                # Compare floats with relative tolerance
                if isinstance(d1[i], float):
                    # If d2 is not a float, mark and check next
                    if not isinstance(d2[i], float):
                        differences.append(f"-{full_path}: {repr(d1[i])}")
                        differences.append(f"+{full_path}: {repr(d2[i])}")
                        continue
                    if isinstance(d2[i], float) and math.isclose(
                        d1[i], d2[i], rel_tol=rel_tol
                    ):
                        print(f"\n-{full_path}: {repr(d1[i])}")
                        print(
                            f"+{full_path}: {repr(d2[i])} (are close with rel_tol: {rel_tol})"
                        )
                    else:
                        rel_err = abs(d1[i] - d2[i]) / (
                            max(abs(d1[i]), abs(d2[i]))
                        )
                        differences.append(f"-{full_path}: {repr(d1[i])}")
                        differences.append(
                            f"+{full_path}: {repr(d2[i])} (rel_err: {rel_err})"
                        )
                # Recursively handle nested lists/tuples
                elif isinstance(d1[i], list) or isinstance(d1[i], tuple):
                    # If d2 is not a list/tuple, mark and check next
                    if not (
                        isinstance(d2[i], list) or isinstance(d2[i], tuple)
                    ):
                        differences.append(f"-{full_path}: {repr(d1[i])}")
                        differences.append(f"+{full_path}: {repr(d2[i])}")
                        continue
                    nested_diff = dict_diff(d1[i], d2[i], full_path, rel_tol)
                    differences.extend(nested_diff)
                # Recursively handle nested dicts
                elif isinstance(d1[i], dict):
                    # If d2 is not a dict, mark and check next
                    if not isinstance(d2[i], dict):
                        differences.append(f"-{full_path}: {repr(d1[i])}")
                        differences.append(f"+{full_path}: {repr(d2[i])}")
                        continue
                    nested_diff = dict_diff(d1[i], d2[i], full_path, rel_tol)
                    differences.extend(nested_diff)
                # Other types
                else:
                    differences.append(f"-{full_path}: {repr(d1[i])}")
                    differences.append(f"+{full_path}: {repr(d2[i])}")
            # else:
            #     print(f"\n*{full_path}: {repr(d1[i])} (identical)")
        return differences

    # If d1 or d2 is not a dict
    if not (isinstance(d1, dict) and isinstance(d2, dict)):
        # If different, mark and return
        if d1 != d2:
            differences.append(f"-{path}: {repr(d1)}")
            differences.append(f"+{path}: {repr(d2)}")
        return differences

    # Keys in d1 but not in d2
    for k in sorted(set(d1) - set(d2)):
        full_path = f"{path}.{k}" if path else k
        differences.append(f"-{full_path}: {repr(d1[k])}")

    # Keys in d2 but not in d1
    for k in sorted(set(d2) - set(d1)):
        full_path = f"{path}.{k}" if path else k
        differences.append(f"+{full_path}: {repr(d2[k])}")

    # Keys in both, check each value
    for k in sorted(set(d1) & set(d2)):
        full_path = f"{path}.{k}" if path else k
        if d1[k] != d2[k]:
            # Compare floats with relative tolerance
            if isinstance(d1[k], float):
                # If d2 is not a float, mark and check next
                if not isinstance(d2[k], float):
                    differences.append(f"-{full_path}: {repr(d1[k])}")
                    differences.append(f"+{full_path}: {repr(d2[k])}")
                    continue
                if math.isclose(d1[k], d2[k], rel_tol=rel_tol):
                    print(f"\n-{full_path}: {repr(d1[k])}")
                    print(
                        f"+{full_path}: {repr(d2[k])} (are close with rel_tol: {rel_tol})"
                    )
                else:
                    rel_err = abs(d1[k] - d2[k]) / (
                        max(abs(d1[k]), abs(d2[k]))
                    )
                    differences.append(f"-{full_path}: {repr(d1[k])}")
                    differences.append(
                        f"+{full_path}: {repr(d2[k])} (rel_err: {rel_err})"
                    )
            # Recursively handle nested lists/tuples
            elif isinstance(d1[k], list) or isinstance(d1[k], tuple):
                # If d2 is not a list/tuple, mark and check next
                if not (isinstance(d2[k], list) or isinstance(d2[k], tuple)):
                    differences.append(f"-{full_path}: {repr(d1[k])}")
                    differences.append(f"+{full_path}: {repr(d2[k])}")
                    continue
                nested_diff = dict_diff(d1[k], d2[k], full_path, rel_tol)
                differences.extend(nested_diff)
            # Recursively handle nested dicts
            elif isinstance(d1[k], dict):
                # If d2 is not a dict, mark and check next
                if not isinstance(d2[k], dict):
                    differences.append(f"-{full_path}: {repr(d1[k])}")
                    differences.append(f"+{full_path}: {repr(d2[k])}")
                    continue
                nested_diff = dict_diff(d1[k], d2[k], full_path, rel_tol)
                differences.extend(nested_diff)
            # Other types
            else:
                differences.append(f"-{full_path}: {repr(d1[k])}")
                differences.append(f"+{full_path}: {repr(d2[k])}")
        # else:
        #     print(f"\n*{full_path}: {repr(d1[k])} (identical)")

    return differences
