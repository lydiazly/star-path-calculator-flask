# -*- coding: utf-8 -*-
# core/data_loader.py

"""Loads data and initiates global variables `eph`, `earth`, and `hip_df`.

Example usage:
>>> import core.data_loader as dl
>>> earth = dl.earth
>>> earth.target_name
'399 EARTH'
"""

import os
from pathlib import Path
from skyfield.api import Loader
from skyfield.data import hipparcos

from config import EPH_DATA_FILE, HIP_DATA_FILE

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

# Read from env or in a subfolder 'data/' in the working directory
DATA_DIR: Path = Path(os.getenv('STAR_PATH_DATA_DIR', Path.cwd() / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
# print(f"[Data Location] {DATA_DIR}")

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
    except Exception as e:
        raise Exception(f"Failed to load ephemeris data: {str(e)}")

    # Load the Hipparcos Catalogue dataframe --------------------------|
    hip_full_path: Path = DATA_DIR / HIP_DATA_FILE
    try:
        url_or_path = HIP_DATA_FILE if hip_full_path.is_file() else hipparcos.URL
        # Load from or download to DATA_DIR
        with load.open(url_or_path) as f:
            hip_df = hipparcos.load_dataframe(f)
    except Exception as e:
        raise Exception(f"Failed to load Hipparcos Catalogue: {str(e)}")
