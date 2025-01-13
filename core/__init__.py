# core/__init__.py
"""Main module for calculating seasons and plotting star paths.

Files:
    data_loader.py: Loads data and initiates global variables `eph`, `earth`, and `hip_df`.
    seasons.py: Calculates the time and coordinates of equinoxes and solstices.
    star_path.py: Plots star paths.

Classes:
    StarObject: Main class for creating a Star object and generating a star path.

Functions:
    load_data: Loads the ephemeris data and the Hipparcos Catalogue.
"""
from .data_loader import load_data

load_data()
