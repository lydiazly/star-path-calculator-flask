# -*- coding: utf-8 -*-
# config/constants.py

__all__ = ["EPH_DATA_FILE", "HIP_DATA_FILE", "HIP_NAME_FILE", "EPH_DATE_MIN", "EPH_DATE_MAX"]


# Data file (https://ssd.jpl.nasa.gov/planets/eph_export.html)
EPH_DATA_FILE = 'de406.bsp'  # JED 0625360.5 (-3000 FEB 23) to 2816912.50 (+3000 MAY 06)
# EPH_DATA_FILE = 'de422.bsp'  # JED 625648.5, (-3000 DEC 07) to JED 2816816.5, (3000 JAN 30)
# EPH_DATA_FILE = 'de440.bsp'  # JED 2287184.5, (1549 DEC 31) to JED 2688976.5, (2650 JAN 25)
HIP_DATA_FILE = 'hip_main.dat'
HIP_NAME_FILE = 'hip_ident.csv'

# Ephemeris date range
EPH_DATE_MIN = [-3000, 1, 29]  # 29 January 3001 BCE (Gregorian)
EPH_DATE_MAX = [3000, 5, 6]  # 6 May 3000 CE
