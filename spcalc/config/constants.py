# -*- coding: utf-8 -*-
# config/constants.py

__all__ = ["EPH_DATE_MIN", "EPH_DATE_MAX", "CC_YEAR_RANGE", "POINTS"]

# Ephemeris date range
EPH_DATE_MIN = [-3000, 1, 29]  # 29 January 3001 BCE (Gregorian)
EPH_DATE_MAX = [3000, 5, 6]  # 6 May 3000 CE

# The available year range in Chinese calendar
CC_YEAR_RANGE = [-721, 2200]

POINTS = {
    'R': "Rising",
    'T': "Meridian transit",
    'S': "Setting",
    'N0': "Sunset",
    'N1': "Civil dusk ends",
    'N2': "Nautical dusk ends",
    'N3': "Astronomical dusk ends",
    'D3': "Astronomical dawn starts",
    'D2': "Nautical dawn starts",
    'D1': "Civil dawn starts",
    'D0': "Sunrise",
}
