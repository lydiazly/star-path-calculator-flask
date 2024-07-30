# -*- coding: utf-8 -*-
# config/constants.py

__all__ = ["EPH_DATA_FILE", "HIP_DATA_FILE", "HIP_BAYER_FILE", "HIP_PROPER_FILE", "EPH_DATE_MIN", "EPH_DATE_MAX"]


# Data file
EPH_DATA_FILE = 'de406.bsp'
HIP_DATA_FILE = 'hip_main.dat'
HIP_BAYER_FILE = 'ident_bayer.pkl'
HIP_PROPER_FILE = 'ident_proper.pkl'

# Ephemeris date range
EPH_DATE_MIN = [-3000, 1, 29]  # 29 January 3001 BCE
EPH_DATE_MAX = [3000, 5, 6]  # 6 May 3000 CE
