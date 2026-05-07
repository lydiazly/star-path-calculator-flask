# -*- coding: utf-8 -*-
# core/data_loader.py

"""Loads data and initiates global variables `eph`, `earth`, and `hip_df`.

Example usage:
>>> import starpathcalculator.core.data_loader as dl
>>> earth = dl.earth
>>> earth.target_name
'399 EARTH'
"""

import os
from pathlib import Path
from skyfield.api import Loader
from skyfield.data import hipparcos

__all__ = [
    "DATA_DIR",
    "load",
    "timescale",
    "eph",
    "earth",
    "hip_df",
    "load_data",
    "cal_hans",
    "cal_hant",
]

# Load variables from .env into os.environ
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


# Ephemeris data (https://ssd.jpl.nasa.gov/planets/eph_export.html)
EPH_DATA_FILE = "de406.bsp"  # JED 0625360.5 (-3000 FEB 23) to 2816912.50 (+3000 MAY 06)
# EPH_DATA_FILE = "de422.bsp"  # JED 625648.5, (-3000 DEC 07) to JED 2816816.5, (3000 JAN 30)
# EPH_DATA_FILE = "de440.bsp"  # JED 2287184.5, (1549 DEC 31) to JED 2688976.5, (2650 JAN 25)

# The Hipparcos and Tycho catalogues (https://cdsarc.cds.unistra.fr/ftp/cats/I/239)
HIP_DATA_FILE = "hip_main.dat"  # 25-Jun-1997

# Read from env or in a subfolder 'data/' in the current working directory
DATA_DIR: Path = Path(os.getenv('STAR_PATH_DATA_DIR', Path.cwd() / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
# print(f"[Data location] {DATA_DIR}")

# Set the loader with the data location
load = Loader(str(DATA_DIR))

timescale = load.timescale()

# Global variables
eph = None
"""The ephemeris data."""
earth = None
"""The Earth object."""
hip_df = None
"""The Hipparcos Catalogue dataframe."""

try:
    import ChineseCalendar_py.calendar_conversion as ccal

    cal_hans = ccal.calendar_conversion('ChiS')
    cal_hant = ccal.calendar_conversion('ChiT')
except Exception:
    cal_hans = None
    cal_hant = None


def load_data() -> None:
    """Loads the ephemeris data and the Hipparcos Catalogue."""
    global eph, earth, hip_df

    # Load the ephemeris data -----------------------------------------|
    try:
        # Load from or download to DATA_DIR
        eph = load(EPH_DATA_FILE)
        earth = eph['earth']
        if eph is None or earth is None:
            raise ValueError("Loaded ephemeris data is invalid.")
    except Exception as e:
        raise Exception(f"Failed to load ephemeris data: {str(e)}")

    # Load the Hipparcos Catalogue dataframe --------------------------|
    hip_full_path: Path = DATA_DIR / HIP_DATA_FILE
    try:
        url_or_path = HIP_DATA_FILE if hip_full_path.is_file() else hipparcos.URL
        # Load from or download to DATA_DIR
        with load.open(url_or_path) as f:
            hip_df = hipparcos.load_dataframe(f)
        if hip_df is None:
            raise ValueError("Loaded Hipparcos Catalogue is invalid.")
    except Exception as e:
        raise Exception(f"Failed to load Hipparcos Catalogue: {str(e)}")
