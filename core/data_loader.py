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
import os
from config import constants

__all__ = ["load_data",]


# Global variables
eph = None
earth = None


# Load the ephemeris data
def load_data():
    global eph, earth

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(parent_dir, 'data')
    data_full_path = os.path.join(data_dir, constants.DATA_FILE)
    os.makedirs(data_dir, exist_ok=True)

    try:
        if not os.path.isfile(data_full_path):
            original_dir = os.getcwd()
            os.chdir(data_dir)
            eph = load(constants.DATA_FILE)
            os.chdir(original_dir)
        else:
            eph = load_file(data_full_path)
        earth = eph['earth']
    except Exception as e:
        raise Exception(f"Failed to load ephemeris data: {str(e)}")
