# -*- coding: utf-8 -*-
# utils/script_utils.py
"""
Functions used only for scripts that are executed from the command line.
"""

from typing import List
import calendar
import pandas as pd
# import pickle
import os
from config import EPH_DATE_MIN, EPH_DATE_MAX, HIP_BAYER_FILE, HIP_PROPER_FILE

__all__ = ["format_datetime", "format_datetime_iso", "validate_datetime", "validate_year"]


# Formats the date and time into strings as '1 Jan 2000 CE' and '12:00:00[.000]'
def format_datetime(year: int, month: int = 1, day: int = 1,
                    hour: int = 12, minute: int = 0, second: float = 0,
                    month_first = False, abbr = True, year_only = False) -> List[str]:
    year_str = f"{year} CE" if year > 0 else f"{-year + 1} BCE"
    month_str = calendar.month_abbr[month] if abbr else calendar.month_name[month]
    date_str = f"{month_str} {day}, {year_str}" if month_first else f"{day} {month_str} {year_str}"
    sec_str = f"{int(second):02d}" if float(second).is_integer() else f"{second:06.3f}"
    time_str = f"{hour:02d}:{minute:02d}:{sec_str}"
    return [year_str] if year_only else [date_str, time_str]


# Formats the date and time into ISO format strings '2000-01-01 12:00:00[.000]'
def format_datetime_iso(year: int, month: int = 1, day: int = 1,
                        hour: int = 12, minute: int = 0, second: float = 0) -> List[str]:
    date_str = f"{year}-{month:02d}-{day:02d}"
    sec_str = f"{int(second):02d}" if float(second).is_integer() else f"{second:06.3f}"
    time_str = f"{hour:02d}:{minute:02d}:{sec_str}"
    return [date_str, time_str]


EPH_DATE_MIN_STR, _ = format_datetime_iso(*EPH_DATE_MIN)
EPH_DATE_MAX_STR, _ = format_datetime_iso(*EPH_DATE_MAX)


def validate_datetime(year: int, month: int, day: int,
                      hour: int = 12, minute: int = 0, second: float = 0):
    day_max = 31
    if month == 2:
        day_max = 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
    elif month in [4, 6, 9, 11]:
        day_max = 30

    if not (1 <= month <= 12 and 1 <= day <= day_max):
        raise ValueError(f"Invalid date: [year, month, day] = [{year}, {month}, {day}]")

    if not (0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60):
        raise ValueError(f"Invalid time: {hour}:{minute}:{second}")

    if (
        year < EPH_DATE_MIN[0]
        or (year == EPH_DATE_MIN[0]
            and (month < EPH_DATE_MIN[1]
                or (month == EPH_DATE_MIN[1] and day < EPH_DATE_MIN[2])))
    ) or (
        year > EPH_DATE_MAX[0]
        or (year == EPH_DATE_MAX[0]
            and (month > EPH_DATE_MAX[1]
                or (month == EPH_DATE_MAX[1] and day > EPH_DATE_MAX[2])))
    ):
        raise ValueError(f"Out of the ephemeris date range: {EPH_DATE_MIN_STR} \u2013 {EPH_DATE_MAX_STR}")


def validate_year(year: int):
    if (year <= EPH_DATE_MIN[0] or year >= EPH_DATE_MAX[0]):
        raise ValueError(f"Out of the ephemeris date range: {EPH_DATE_MIN_STR} \u2013 {EPH_DATE_MAX_STR}")


def check_year(year: int, month: int, day: int,
               hour: int = 12, minute: int = 0, second: float = 0):
    day_max = 31
    if month == 2:
        day_max = 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
    elif month in [4, 6, 9, 11]:
        day_max = 30

    if not (1 <= month <= 12 and 1 <= day <= day_max):
        raise ValueError(f"Invalid date: [year, month, day] = [{year}, {month}, {day}]")

    if not (0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60):
        raise ValueError(f"Invalid time: {hour}:{minute}:{second}")

    if (
        year < EPH_DATE_MIN[0]
        or (year == EPH_DATE_MIN[0]
            and (month < EPH_DATE_MIN[1]
                or (month == EPH_DATE_MIN[1] and day < EPH_DATE_MIN[2])))
    ) or (
        year > EPH_DATE_MAX[0]
        or (year == EPH_DATE_MAX[0]
            and (month > EPH_DATE_MAX[1]
                or (month == EPH_DATE_MAX[1] and day > EPH_DATE_MAX[2])))
    ):
        raise ValueError(f"Out of the ephemeris date range: {EPH_DATE_MIN_STR} \u2013 {EPH_DATE_MAX_STR}")


# Converts decimal hours to HMS (Hours, Minutes, Seconds).
def decimal_to_hms(decimal_hours: float) -> dict:
    sign = -1 if decimal_hours < 0 else 1
    abs_decimal_hours = abs(decimal_hours)
    abs_hours = int(abs_decimal_hours)
    minutes = int((abs_decimal_hours - abs_hours) * 60)
    seconds = ((abs_decimal_hours - abs_hours) * 60 - minutes) * 60
    return {'hours': sign * abs_hours, 'minutes': minutes, 'seconds': seconds}


# Formats a decimal UTC offset into a string.
def format_timezone(tz: float) -> str:
    hms = decimal_to_hms(tz)
    return f"{'-' if tz < 0 else '+'}{abs(hms['hours']):02d}:{hms['minutes']:02d}"


def load_hip_ident() -> pd.DataFrame:
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    data_full_path_bayer = os.path.join(data_dir, HIP_BAYER_FILE)
    data_full_path_proper = os.path.join(data_dir, HIP_PROPER_FILE)
    df_bayer = pd.read_pickle(data_full_path_bayer)
    df_proper = pd.read_pickle(data_full_path_proper)
    # with open(data_full_path_bayer, 'rb') as file:
    #     df_bayer = pickle.load(file)
    # with open(data_full_path_proper, 'rb') as file:
    #     df_proper = pickle.load(file)

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

    return df_merged


def hip_to_name(hip: int, df: pd.DataFrame) -> dict:
    # Set 'hip' as the index for faster lookup
    df.set_index('hip', inplace=True)
    if hip in df.index:
        name = df.loc[hip, 'name']
    return name


def df_to_json(df: pd.DataFrame, filename = 'hip_ident.json'):
    import json
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    data_dict = df.to_dict(orient='records')
    with open(os.path.join(data_dir, filename), 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)
