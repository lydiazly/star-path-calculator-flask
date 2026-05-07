# -*- coding: utf-8 -*-
# tests/helpers.py
import math
import pytest


def is_floats_close(a, b, rel_tol, abs_tol, abs_tol_thred) -> tuple[bool, float]:
    """Compares two floats using `math.isclose(a, b, rel_tol, abs_tol)`:
    - If `abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol_default)`
      where `abs_tol_default` is 0, then `a` and `b` are considered "close" to each other.
    - If `max(abs(a), abs(b)) <= abs_tol_thred`, use the given `abs_tol` value in `math.isclose`.

    Returns `(is_close, rel_err, abs_err, is_small)`.
    """
    _max = max(abs(a), abs(b))
    is_small = _max <= abs_tol_thred
    _abs_tol = abs_tol if is_small else 0
    abs_err = abs(a - b)
    rel_err = abs_err / _max
    is_close = math.isclose(a, b, rel_tol=rel_tol, abs_tol=_abs_tol)
    return (is_close, rel_err, abs_err, is_small)


def assert_iterable_equal(
    d1: dict | list,
    d2: dict | list,
    include_keys: list[str] | None = None,
    rel_tol=1e-9,
    abs_tol=1e-7,
    abs_tol_thred=1e-6,
):
    """Asserts that two dictionaries/lists are equal with tolerance for floats.
    Floats are compared based on their string representation with
    the specified number of significant digits.
    - `abs_tol` is only used when a absolute value is no greater than `abs_tol_thred`.
    - If `include_keys` is not `None`, only compare these keys.
    """
    differences = iterable_diff(
        d1,
        d2,
        include_keys=include_keys,
        rel_tol=rel_tol,
        abs_tol=abs_tol,
        abs_tol_thred=abs_tol_thred,
    )
    if differences:
        formatted_diff = ["", "--- dict1 (actual)", "+++ dict2 (expected)", ""]
        formatted_diff.extend(differences)
        pytest.fail("\n".join(formatted_diff))


def iterable_diff(
    d1, d2, path="", include_keys=None, rel_tol=1e-9, abs_tol=1e-7, abs_tol_thred=1e-6
):
    """Recursively finds differences between two nested lists/tuples/dicts."""
    differences = []

    # Lists -----------------------------------------------------------|
    # If d1 is a list/tuple
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
                    # If both are floats, compare
                    is_close, rel_err, abs_err, is_small = is_floats_close(
                        d1[i], d2[i], rel_tol, abs_tol, abs_tol_thred
                    )
                    if is_small:
                        err_msg = f"abs_err: {abs_err:e}"
                    else:
                        err_msg = f"rel_err: {rel_err:e}"
                    if is_close:
                        print(f"\n-{full_path}: {repr(d1[i])}")
                        print(f"+{full_path}: {repr(d2[i])} (close but {err_msg})")
                    else:
                        differences.append(f"-{full_path}: {repr(d1[i])}")
                        differences.append(f"+{full_path}: {repr(d2[i])} ({err_msg})")
                # Recursively handle nested lists/tuples
                elif isinstance(d1[i], list) or isinstance(d1[i], tuple):
                    # If d2 is not a list/tuple, mark and check next
                    if not (isinstance(d2[i], list) or isinstance(d2[i], tuple)):
                        differences.append(f"-{full_path}: {repr(d1[i])}")
                        differences.append(f"+{full_path}: {repr(d2[i])}")
                        continue
                    nested_diff = iterable_diff(
                        d1[i],
                        d2[i],
                        full_path,
                        include_keys,
                        rel_tol,
                        abs_tol,
                        abs_tol_thred,
                    )
                    differences.extend(nested_diff)
                # Recursively handle nested dicts
                elif isinstance(d1[i], dict):
                    # If d2 is not a dict, mark and check next
                    if not isinstance(d2[i], dict):
                        differences.append(f"-{full_path}: {repr(d1[i])}")
                        differences.append(f"+{full_path}: {repr(d2[i])}")
                        continue
                    nested_diff = iterable_diff(
                        d1[i],
                        d2[i],
                        full_path,
                        include_keys,
                        rel_tol,
                        abs_tol,
                        abs_tol_thred,
                    )
                    differences.extend(nested_diff)
                # Other types
                else:
                    differences.append(f"-{full_path}: {repr(d1[i])}")
                    differences.append(f"+{full_path}: {repr(d2[i])}")
            # else:
            #     print(f"\n*{full_path}: {repr(d1[i])} (identical)")
        return differences

    # Dicts -----------------------------------------------------------|
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
        if include_keys is not None and len(include_keys) > 0 and k not in include_keys:
            continue
        full_path = f"{path}.{k}" if path else k
        if d1[k] != d2[k]:
            # Compare floats with relative tolerance
            if isinstance(d1[k], float):
                # If d2 is not a float, mark and check next
                if not isinstance(d2[k], float):
                    differences.append(f"-{full_path}: {repr(d1[k])}")
                    differences.append(f"+{full_path}: {repr(d2[k])}")
                    continue
                # If both are floats, compare
                is_close, rel_err, abs_err, is_small = is_floats_close(
                    d1[k], d2[k], rel_tol, abs_tol, abs_tol_thred
                )
                if is_small:
                    err_msg = f"abs_err: {abs_err:e}"
                else:
                    err_msg = f"rel_err: {rel_err:e}"
                if is_close:
                    print(f"\n-{full_path}: {repr(d1[k])}")
                    print(f"+{full_path}: {repr(d2[k])} (close but {err_msg})")
                else:
                    differences.append(f"-{full_path}: {repr(d1[k])}")
                    differences.append(f"+{full_path}: {repr(d2[k])} ({err_msg})")
            # Recursively handle nested lists/tuples
            elif isinstance(d1[k], list) or isinstance(d1[k], tuple):
                # If d2 is not a list/tuple, mark and check next
                if not (isinstance(d2[k], list) or isinstance(d2[k], tuple)):
                    differences.append(f"-{full_path}: {repr(d1[k])}")
                    differences.append(f"+{full_path}: {repr(d2[k])}")
                    continue
                nested_diff = iterable_diff(
                    d1[k],
                    d2[k],
                    full_path,
                    include_keys,
                    rel_tol,
                    abs_tol,
                    abs_tol_thred,
                )
                differences.extend(nested_diff)
            # Recursively handle nested dicts
            elif isinstance(d1[k], dict):
                # If d2 is not a dict, mark and check next
                if not isinstance(d2[k], dict):
                    differences.append(f"-{full_path}: {repr(d1[k])}")
                    differences.append(f"+{full_path}: {repr(d2[k])}")
                    continue
                nested_diff = iterable_diff(
                    d1[k],
                    d2[k],
                    full_path,
                    include_keys,
                    rel_tol,
                    abs_tol,
                    abs_tol_thred,
                )
                differences.extend(nested_diff)
            # Other types
            else:
                differences.append(f"-{full_path}: {repr(d1[k])}")
                differences.append(f"+{full_path}: {repr(d2[k])}")
        # else:
        #     print(f"\n*{full_path}: {repr(d1[k])} (identical)")

    return differences
