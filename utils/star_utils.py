# -*- coding: utf-8 -*-
# utils/star_utils.py
"""
Functions handle Hipparchus catalogue number, names, etc.
"""

import pandas as pd
import os
from config import HIP_NAME_FILE

__all__ = ["hip_to_name"]


data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
df_hip_name = pd.read_csv(os.path.join(data_dir, HIP_NAME_FILE))
# Set 'hip' as the index for faster lookup
df_hip_name.set_index('hip', inplace=True)


def hip_to_name(hip: int) -> str:
    try:
        name = df_hip_name.loc[hip, 'name']
    except KeyError:
        name = ""
    return name