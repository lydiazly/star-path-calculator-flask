# -*- coding: utf-8 -*-
# utils/star_utils.py
"""Functions to handle Hipparcos Catalogue number, names, etc."""

import pandas as pd

from starpathcalculator.core.data_loader import DATA_DIR

__all__ = ["hip_to_name"]

# Proper names and Bayer designations (https://cdsarc.cds.unistra.fr/ftp/I/239/version_cd/tables)
HIP_IDENT_FILE = "hip_ident.csv"  # merged

df_hip_name = pd.read_csv(DATA_DIR / HIP_IDENT_FILE)
# Set 'hip' as the index for faster lookup
df_hip_name.set_index('hip', inplace=True)


def hip_to_name(hip: int) -> str:
    """Finds the name of a given HIP."""
    try:
        name = df_hip_name.loc[hip, 'name']
    except KeyError:
        name = ""
    return name
