# -*- coding: utf-8 -*-
# core/data_loader.py

"""
Use global variables eph and earth by referencing, e.g.:
```
import core.data_loader as dl
some_value = dl.eph.some_method()
```
"""

from skyfield.api import load, load_file
from skyfield.data import hipparcos
import os
from config import constants

__all__ = ["load_data",]


# Global variables
eph = None
earth = None
hip_df = None

def load_data():
    global eph, earth, hip_df

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(parent_dir, 'data')
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
    except Exception as e:
        raise Exception(f"Failed to load Hipparcos data: {str(e)}")
