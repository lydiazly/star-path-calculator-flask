# __init__.py
"""Tracks the apparent motions of a celestial object observed from any location on any chosen date."""

__all__ = ['run']
__author__ = 'Stardial'

try:
    from importlib.metadata import version, PackageNotFoundError

    __version__ = version('star-path-calculator')
except PackageNotFoundError:
    __version__ = 'dev'
