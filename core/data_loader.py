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
import pandas as pd
import os
from config import constants

__all__ = ["load_data", "load_hip_ident", "hip_to_name"]


# Global variables
eph = None
earth = None
hip_df = None

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def load_data():
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
    except Exception as e:
        raise Exception(f"Failed to load Hipparcos data: {str(e)}")


def load_hip_ident() -> pd.DataFrame:
    data_full_path_bayer = os.path.join(data_dir, constants.HIP_BAYER_FILE)
    data_full_path_proper = os.path.join(data_dir, constants.HIP_PROPER_FILE)
    df_bayer = pd.read_pickle(data_full_path_bayer)
    df_proper = pd.read_pickle(data_full_path_proper)

    # Group by HIP and aggregate Bayer Designation and Proper Name with '/'
    df_bayer_agg = df_bayer.groupby('HIP')['Bayer Designation'].apply(lambda x: '/'.join(x)).reset_index()
    df_proper_agg = df_proper.groupby('HIP')['Proper Name'].apply(lambda x: '/'.join(x)).reset_index()

    # Merge the aggregated DataFrames on the HIP column
    df_merged = pd.merge(df_bayer_agg, df_proper_agg, on='HIP', how='outer')

    # Fill NaN values with empty strings
    df_merged['Bayer Designation'] = df_merged['Bayer Designation'].fillna('')
    df_merged['Proper Name'] = df_merged['Proper Name'].fillna('')

    # Combine bayer and proper into a single 'name' column
    df_merged['name'] = df_merged['Bayer Designation'] + '/' + df_merged['Proper Name']
    df_merged['name'] = df_merged['name'].str.strip('/').str.replace('//', '/')

    # Select only the required columns and rename them
    df_merged = df_merged[['HIP', 'name']]
    df_merged.columns = ['hip', 'name']

    # Set 'hip' as the index for faster lookup
    df_merged.set_index('hip', inplace=True)

    return df_merged

def hip_to_name(hip: int, df_merged: pd.DataFrame) -> dict:
    result = {'hip': hip, 'name': ''}
    if hip in df_merged.index:
        result['name'] = df_merged.loc[hip, 'name']
    return result

def df_to_json(df: pd.DataFrame, filename = 'hip_ident.json'):
    import json
    data_dict = df.to_dict(orient='records')
    with open(os.path.join(data_dir, filename), 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)