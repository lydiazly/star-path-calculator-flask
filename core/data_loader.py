# -*- coding: utf-8 -*-
# core/data_loader.py

"""Loads data and initiates global variables `eph`, `earth`, and `hip_df`.

Example usage:
    >>> import core.data_loader as dl
    >>> earth = dl.earth
    >>> earth.target_name
    '399 EARTH'
"""
from skyfield.api import load, load_file
from skyfield.data import hipparcos
import os
from config import constants

__all__ = ["eph", "earth", "hip_df", "load_data"]


# Global variables
eph = None
earth = None
hip_df = None

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def load_data():
    """Loads the ephemeris data and the Hipparcos Catalogue."""
    global eph, earth, hip_df

    os.makedirs(data_dir, exist_ok=True)

    # Load the ephemeris data -------------------------------------------------|
    data_full_path = os.path.join(data_dir, constants.EPH_DATA_FILE)
    try:
        if not os.path.isfile(data_full_path):
            original_dir = os.getcwd()
            os.chdir(data_dir)
            eph = load(constants.EPH_DATA_FILE)
            os.chdir(original_dir)
        else:
            eph = load_file(data_full_path)
        earth = eph['earth']
    except Exception as e:
        raise Exception(f"Failed to load ephemeris data: {str(e)}")

    # Load the Hipparcos data -------------------------------------------------|
    data_full_path = os.path.join(data_dir, constants.HIP_DATA_FILE)
    try:
        if not os.path.isfile(data_full_path):
            original_dir = os.getcwd()
            os.chdir(data_dir)
            _f = load.open(hipparcos.URL, filename=constants.HIP_DATA_FILE)
            os.chdir(original_dir)
        else:
            _f = load.open(data_full_path)
        hip_df = hipparcos.load_dataframe(_f)
        _f.close()
    except Exception as e:
        raise Exception(f"Failed to load Hipparcos data: {str(e)}")
