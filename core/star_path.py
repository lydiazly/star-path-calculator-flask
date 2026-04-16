# -*- coding: utf-8 -*-
# core/star_path.py
"""Functions to plot star paths.

Refer to the global variables `eph`, `earth`, and `hip_df` by:
>>> import core.data_loader as dl
>>> eph = dl.eph
>>> earth = dl.earth
>>> hip_df = dl.hip_df
"""

import matplotlib

matplotlib.use('Agg')  # Use the Agg backend for non-interactive plotting

import base64
from datetime import datetime
import io
from matplotlib.figure import Figure
import matplotlib.patheffects as path_effects
from matplotlib.projections.polar import PolarAxes
import matplotlib.pyplot as plt
from matplotlib.text import Text
import numpy as np
from numpy.typing import NDArray
import re
from skyfield import almanac
from skyfield.api import Star, wgs84
from skyfield.timelib import Time
from skyfield.units import Angle
from typing import TypeAlias

import core.data_loader as dl
from utils.time_utils import (
    get_standard_offset_by_id,
    ut1_to_standard_time,
    ut1_to_local_mean_time,
)
import juliandate
from great_circle_calculator.great_circle_calculator import (
    distance_between_points,
    intermediate_point,
)

__all__ = ["get_diagram"]


STAR_NEVER_RISES_MSG = "WARNING: This star never rises at this location on this date."

# Manually set the atmospheric refractive angle at the horizon to 34.452 arcminutes
horizon_degrees = -0.5666 - 0.0076

label_fontsize = 10

timescale = dl.timescale

# Ensure ephemeris data is loaded
if dl.eph is None or dl.earth is None:
    dl.load_data()
    # print("Warning: Ephemeris data was not loaded. `core.data_loader.load_data()` is called.")

# Type alias
Annotations: TypeAlias = list[dict[str, str | bool | float | tuple[int, ...]]]


# ---------------------------------------------------------------------|
class StarObject:
    """Main class for creating a Star object and generating a star path.
    - The input date is assumed to be in Standard Time for a given time zone ID.
    - The time zone IDs and standard offsets in this project are **only** used for
      the Standard Time output and the time window setting to calculate the rising/setting times.

    Attributes:
        year (int): Year. 0 is 1 BCE.
        month (int): Month. Starts from 1 (January).
        day (int): Day of the month.
        lat (float): Latitude (-90 <= `lat` <= 90).
        lng (float): Longitude (-180 <= `lng` <= 180).
        tz_id (str): The time zone ID.
        name (str | None): The star name. Defaults to `None`.
        hip (int): The star's HIP number. Defaults to -1 (means N/A).
        radec (tuple[float, float] | None): The RA/Dec in decimal degrees. Defaults to `None`.
        offset_in_minutes (float): The Standard Time offset in minutes.
        tz_name (str): The current time zone name of this location.
            If the offset is non-standard, returns 'LMT'.
        star: The star object.
        loc: The GeographicPosition object for the given latitude and longitude.
        observer: The observer object on the Earth's surface.
    """

    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        lat: float,
        lng: float,
        tz_id: str,
        name: str | None = None,
        hip: int = -1,
        radec: tuple[float, float] | None = None,
    ):
        self.year: int = year
        self.month: int = month
        self.day: int = day
        self.lat: float = lat
        self.lng: float = lng
        self.tz_id = tz_id
        self.name: str | None = name  # will be converted to lowercase
        self.hip = hip
        self.radec = radec

        self.offset_in_minutes: float
        self.tz_name: str
        self.offset_in_minutes, self.tz_name = get_standard_offset_by_id(tz_id)

        self.star = self._initialize_star()  # type: ignore[no-untyped-call]
        self.loc = wgs84.latlon(longitude_degrees=lng, latitude_degrees=lat)
        self.observer = dl.earth + self.loc

        self._t0: Time = timescale.ut1(
            year, month, day, 0, 0 - self.offset_in_minutes, 0
        )
        """The starting time for calculating rising/setting times, assumed to be
        at 0:00:00 in Standard Time.
        """
        self._t1: Time = timescale.ut1_jd(self._t0.ut1 + 3)
        """The ending time for calculating rising/setting times, assumed to be
        3 days later.
        """

    def _initialize_star(self):  # type: ignore[no-untyped-def]
        s = None
        if self.name is not None:
            self.name = self.name.lower()
            if self.name in ['mercury', 'venus', 'mars']:
                # skyfield.vectorlib.VectorSum
                s = dl.eph[self.name]  # type: ignore[index]
            elif self.name in ['jupiter', 'saturn', 'uranus', 'neptune', 'pluto']:
                # skyfield.jpllib.ChebyshevPosition
                s = dl.eph[self.name + ' barycenter']  # type: ignore[index]
            else:
                raise ValueError(f"Invalid planet name: {self.name}")
        elif self.hip >= 0:
            if self.hip < 1 or self.hip > 118322:
                raise ValueError(
                    "The Hipparcos Catalogue number must be in the range [1, 118322]."
                )
            try:
                _s = dl.hip_df.loc[self.hip]  # type: ignore[attr-defined]
                if np.isnan(_s['ra_degrees']):
                    raise ValueError(
                        "WARNING: No RA/Dec data available for this star in the Hipparcos Catalogue."
                    )
                # skyfield.starlib.Star
                s = Star.from_dataframe(_s)
            except KeyError:
                raise ValueError("WARNING: Entry not found in the Hipparcos Catalogue.")
        elif self.radec and len(self.radec) == 2:
            # The unit of RA is converted from degrees to hours
            # skyfield.starlib.Star
            s = Star(
                ra_hours=float(self.radec[0] / 360 * 24),
                dec_degrees=float(self.radec[1]),
            )

        if not s:
            raise ValueError("Invalid celestial object.")

        return s

    def generate_result(self) -> dict[str, str | float | Annotations]:
        """Generates the diagram and annotations.

        Returns:
            dict: A dict containing:
                {
                    'diagram_id': str,
                    'svg_data': str,
                    'annotations': Annotations,
                    'offset': float,
                    'tz_name': str,
                }
        """
        diagram_id, svg_data, points = self._get_star_path_diagram()
        annotations = self._get_annotations(points)

        return {
            'diagram_id': diagram_id,
            'svg_data': svg_data,
            'annotations': annotations,
            'offset': self.offset_in_minutes,
            'tz_name': self.tz_name,
        }

    def _get_star_altaz(self, t: Time) -> tuple[Angle, Angle]:
        """Gets the altazimuth coordinates of a star at a specific moment.

        The horizon angles are not considered.
        The atmospheric refraction is included by setting parameter `temperature_C` to 'standard' (10°C).
        By default, Skyfield uses the observer's elevation above sea level to estimate the atmospheric pressure.
        """
        alt: Angle
        az: Angle
        alt, az, dist = (
            self.observer.at(t)
            .observe(self.star)
            .apparent()
            .altaz(temperature_C='standard')
        )

        return alt, az

    def _get_twilight_time(
        self, t0: Time, t1: Time
    ) -> tuple[list[Time], list[np.int64]]:
        """Gets twilight transition times."""
        f = almanac.dark_twilight_day(dl.eph, self.loc)
        # f returns these values:
        # 0 — Dark of night
        # 1 — Astronomical twilight (less than 18 degrees below the horizon)
        # 2 — Nautical twilight (less than 12 degrees below the horizon)
        # 3 — Civil twilight (less than 6 degrees below the horizon)
        # 4 — Sun is up
        ts: Time
        events: NDArray[np.int64] | list[np.int64]
        ts, events = almanac.find_discrete(t0, t1, f)

        ts1: list[Time] = []
        if len(ts) == 0:
            ts1.append(t0)
            ts1.append(t1)
            events = list(events)
            events.append(f(t0).item())
            events.append(f(t1).item())
            return ts1, events

        else:
            t_cals = ts.ut1_calendar()
            for i in range(len(ts)):
                t_cal = (
                    t_cals[0][i],
                    t_cals[1][i],
                    t_cals[2][i],
                    t_cals[3][i],
                    t_cals[4][i],
                    t_cals[5][i],
                )
                ts1.append(timescale.ut1(*t_cal))

            # Add t0 before the beginning of the list
            # Add t1 behind the ending of the list
            ts1.insert(0, t0)
            ts1.append(t1)
            events = list(events)
            events.insert(0, f(t0).item())
            events.append(f(t1).item())

            return ts1, events

    def _get_star_rising_time(self) -> tuple[Time, np.bool_]:
        """Gets the target's rising time. The path is calculated from this moment.
        Returns:
            tuple: A tuple containing:
                t_rising (Time): The first rising time of this target.
                y_rising (np.bool_): `True` if the target really crosses the horizon,
                    and `False` if the target merely transits without actually touching the horizon.
        """
        t_risings: Time
        y_risings: NDArray[np.bool_]
        t_risings, y_risings = almanac.find_risings(
            self.observer,
            self.star,
            self._t0,
            self._t1,
            horizon_degrees=horizon_degrees,
        )

        return t_risings[0], y_risings[0]

    def _get_star_setting_time(self, t_rising: Time) -> tuple[Time, np.bool_]:
        """Gets the target's setting time. The path's calculation ends at this moment.

        Returns:
            tuple: A tuple containing:
                t_setting (Time): The setting time of this target.
                y_setting (np.bool_): `True` if the target really crosses the horizon,
                    and `False` if the target merely transits without actually touching the horizon.
        """
        t_settings: Time
        y_settings: NDArray[np.bool_]
        t_settings, y_settings = almanac.find_settings(
            self.observer,
            self.star,
            self._t0,
            self._t1,
            horizon_degrees=horizon_degrees,
        )
        # Find the time next to the rising time
        ti: Time
        for i, ti in zip(range(len(t_settings)), t_settings):
            if ti.ut1 - t_rising.ut1 > 1e-6:
                break

        return t_settings[i], y_settings[i]

    def _get_star_meridian_transit_time(self, t_rising: Time) -> Time:
        """Gets the star's meridian transit time."""
        t0: Time = t_rising
        t1: Time = timescale.ut1_jd(t0.ut1 + 2)

        t_transits: Time = almanac.find_transits(self.observer, self.star, t0, t1)

        return t_transits[0]

    def _get_twilight_transition_points(
        self, ts: list[Time], events: list[np.int64]
    ) -> tuple[list[str], list[np.float64], list[np.float64], list[Time]]:
        """Gets transition points between different twilight conditions."""
        names: list[str] = []
        altitudes: list[np.float64] = []
        azimuths: list[np.float64] = []
        times: list[Time] = []

        for i in range(1, len(ts) - 1):
            alt, az = self._get_star_altaz(ts[i])

            if events[i - 1] == 4 and events[i] == 3:
                names.append('N1')
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                times.append(ts[i])
            if events[i - 1] == 3 and events[i] == 2:
                names.append('N2')
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                times.append(ts[i])
            if events[i - 1] == 2 and events[i] == 1:
                names.append('N3')
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                times.append(ts[i])
            if events[i - 1] == 1 and events[i] == 2:
                names.append('D1')
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                times.append(ts[i])
            if events[i - 1] == 2 and events[i] == 3:
                names.append('D2')
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                times.append(ts[i])
            if events[i - 1] == 3 and events[i] == 4:
                names.append('D3')
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                times.append(ts[i])

        return names, altitudes, azimuths, times

    def _plot_in_style(
        self, ax: PolarAxes, event: np.int64, t_jd0: np.float64, t_jd1: np.float64
    ) -> None:
        """Plots the star path in different styles for different twilight stages.

        Input times are in units of Julian days.
        """
        pts_num = int((t_jd1 - t_jd0) * 100)
        t_jds = np.linspace(t_jd0, t_jd1, pts_num if pts_num > 10 else 10)

        altitudes: NDArray[np.float64] = np.zeros(shape=(0), dtype=float)
        azimuths: NDArray[np.float64] = np.zeros(shape=(0), dtype=float)
        for ti in t_jds:
            alt, az = self._get_star_altaz(timescale.ut1_jd(ti))
            altitudes = np.append(altitudes, [alt.degrees])
            azimuths = np.append(azimuths, [az.degrees])

        r_mesh: NDArray[np.float64] = 90.0 - altitudes
        theta_mesh: NDArray[np.float64] = np.radians(azimuths)

        if event == 0 or event == 1:
            (line,) = ax.plot(theta_mesh, r_mesh, 'k-', lw=2)
        elif event == 2:
            (line,) = ax.plot(theta_mesh, r_mesh, 'k--', lw=2, dashes=[2, 2])
        elif event == 3:
            (line,) = ax.plot(theta_mesh, r_mesh, 'k--', lw=2, dashes=[2, 2], alpha=0.4)
        elif event == 4:
            (line,) = ax.plot(theta_mesh, r_mesh, 'k--', lw=0.5, dashes=[1, 4])

    def _plot_meridian_transit_points(
        self, ax: PolarAxes, t_transit: Time
    ) -> tuple[np.float64, np.float64]:
        """Gets meridian transit points (once in a day)."""
        alt, az = self._get_star_altaz(t_transit)

        r: np.float64 = 90.0 - alt.degrees
        theta: np.float64 = np.radians(az.degrees)

        ax.plot(theta, r, 'ro', ms=6)
        if self.lat >= 0:
            ax.annotate(
                'T',
                (theta, r),
                textcoords="offset points",
                xytext=(0, 15),
                ha='center',
                va='top',
                fontsize=label_fontsize,
                color='r',
            )
        else:
            ax.annotate(
                'T',
                (theta, r),
                textcoords="offset points",
                xytext=(0, -16),
                ha='center',
                va='bottom',
                fontsize=label_fontsize,
                color='r',
            )

        return alt.degrees, az.degrees

    def _plot_twilight_transition_points(
        self,
        fig: Figure,
        ax: PolarAxes,
        altitudes: list[np.float64],
        azimuths: list[np.float64],
        names: list[str],
    ) -> None:
        """Plots twilight transition points as well as their labels."""
        if len(altitudes) == 0:
            return

        rs: NDArray[np.float64] = 90.0 - np.array(altitudes)
        thetas: NDArray[np.float64] = np.radians(azimuths)

        for i, j, k in zip(thetas, rs, names):
            ax.plot(i, j, 'ro', ms=4)

        # The code below is to temporarily draw the labels of twilight transition points with adjust_text:
        # texts = []
        # for i, j, k in zip(thetas, rs, names):
        #     ax.plot(i, j, 'ro', ms=4)
        #     texts.append(plt.text(i, j, k, ha='center', va='center', color='r'))
        # adjust_text(texts, x=theta_interp, y=r_interp, expand=(2,2), force_static=(1,1), min_arrow_len=10,
        #             arrowprops=dict(arrowstyle="->", color='r', lw=1, shrinkA=0, shrinkB=2, mutation_scale=10))

        # Draw the labels of twilight transition points.
        # Label positions are set at the ends of extended great circle segments
        # between the pole and the points.
        # The `great_circle_calculator` package is used to calculate great circles.
        if self.lat >= 0:
            cp_coord = (0, self.lat)
        else:
            cp_coord = (180, -self.lat)

        label_coord = []
        _offset_scale = 0.6 * 1e6
        for i in range(len(altitudes)):
            if azimuths[i] > 180:
                _ttp_coord = (azimuths[i] - 360, altitudes[i])
            else:
                _ttp_coord = (azimuths[i], altitudes[i])

            _vector_length = distance_between_points(
                cp_coord, _ttp_coord, unit='meters', haversine=True
            )
            if _vector_length < 2.2e6 and i == 0:
                _offset_scale = 1.5 * 1e6
            _label_coord = intermediate_point(
                cp_coord, _ttp_coord, 1 + _offset_scale / _vector_length
            )

            if _label_coord[0] < 0:
                _label_coord = (_label_coord[0] + 360, _label_coord[1])

            label_coord.append(_label_coord)

        ax2 = fig.add_axes((0.0, 0.0, 1.0, 1.0), facecolor=(1, 1, 1, 0))
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)

        for i in range(len(label_coord)):
            _r = 90 - label_coord[i][1]
            _theta = np.radians(label_coord[i][0])
            label_coord_bg: NDArray[np.float64] | list[float] = ax.transData.transform(
                (_theta, _r)
            )
            label_coord_bg = [
                label_coord_bg[0] / fig.bbox.width,
                label_coord_bg[1] / fig.bbox.height,
            ]

            ttp_coord_bg: NDArray[np.float64] | list[float] = ax.transData.transform(
                (thetas[i], rs[i])
            )
            ttp_coord_bg = [
                ttp_coord_bg[0] / fig.bbox.width,
                ttp_coord_bg[1] / fig.bbox.height,
            ]

            ax2.annotate(
                names[i],
                xy=(ttp_coord_bg[0], ttp_coord_bg[1]),
                xytext=(label_coord_bg[0], label_coord_bg[1]),
                arrowprops=dict(
                    color='r', arrowstyle='-', shrinkA=0.2, shrinkB=0.2, lw=0.5
                ),
                va='center',
                ha='center',
                fontsize=label_fontsize,
                color='r',
            )

        ax2.axis('off')

        # Forces all text to be converted into graphical paths without any distortion or special effects
        for text in ax2.texts:
            text.set_path_effects([path_effects.Normal()])

    def _plot_rising_and_setting_points(
        self, fig: Figure, ax: PolarAxes, t0: Time, t1: Time
    ) -> tuple[list[np.float64], list[np.float64], list[Time]]:
        """Plots the star's rising and setting points, whose latitudes are both at the refraction limit.

        Since their coordinates are out of the plotting range, they are plotted on the ax2 layer.
        The ax2 layer is above the ax layer, where the star paths are drawn on.
        """
        alt0, az0 = self._get_star_altaz(t0)
        alt1, az1 = self._get_star_altaz(t1)

        r0: np.float64 = 90.0 - alt0.degrees
        theta0 = np.radians(az0.degrees)
        r1: np.float64 = 90.0 - alt1.degrees
        theta1: np.float64 = np.radians(az1.degrees)

        # Get the coordinates of the points on fig layer, which are originally drawn on the ax layer.
        # Deliver the obtained coordinates to ax2 layer by dividing them with fig's width and height.
        pcoord0 = ax.transData.transform((theta0, r0))
        x0 = pcoord0[0] / fig.bbox.width
        y0 = pcoord0[1] / fig.bbox.height
        pcoord1 = ax.transData.transform((theta1, r1))
        x1 = pcoord1[0] / fig.bbox.width
        y1 = pcoord1[1] / fig.bbox.height

        ax2 = fig.add_axes((0.0, 0.0, 1.0, 1.0), facecolor=(1, 1, 1, 0))
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)

        ax2.plot(x0, y0, 'ro', ms=6)
        ax2.annotate(
            'R',
            (x0, y0),
            textcoords="offset points",
            xytext=(-10, 0),
            ha='right',
            va='center',
            fontsize=label_fontsize,
            color='r',
        )
        ax2.plot(x1, y1, 'ro', ms=6)
        ax2.annotate(
            'S',
            (x1, y1),
            textcoords="offset points",
            xytext=(10, 0),
            ha='left',
            va='center',
            fontsize=label_fontsize,
            color='r',
        )
        ax2.axis('off')

        # Forces all text to be converted into graphical paths without any distortion or special effects
        for text in ax2.texts:
            text.set_path_effects([path_effects.Normal()])

        return ([alt0.degrees, alt1.degrees], [az0.degrees, az1.degrees], [t0, t1])

    def _plot_celestial_poles(self, ax: PolarAxes) -> None:
        """Plots the north/south celestial pole."""
        if self.lat > 0:
            r = 90 - self.lat
            theta = 0
            ax.plot(theta, r, 'b+', ms=8)
            ax.annotate(
                'NCP',
                (theta, r),
                textcoords="offset points",
                xytext=(-6, 0),
                ha='right',
                va='center',
                fontsize=label_fontsize,
                color='b',
            )
        elif self.lat < 0:
            r = 90 + self.lat
            theta = np.radians(180)
            ax.plot(theta, r, 'b+', ms=8)
            ax.annotate(
                'SCP',
                (theta, r),
                textcoords="offset points",
                xytext=(-6, 0),
                ha='right',
                va='center',
                fontsize=label_fontsize,
                color='b',
            )

    def _get_star_path_diagram(
        self,
    ) -> tuple[str, str, list[tuple[str, np.float64, np.float64, Time]]]:
        """Plots the star path.
        - All text objects are converted to into graphical paths to avoid
          distortion and any special effects.
        - The generated SVG is a filesystem safe Base64 string.

        **Known issues**: Matplotlib's default handling of polar plots generates redundant paths
        at the center in SVG. However, there's no decent solution for now, so we just keep them as is.
        """
        t_rising, y_rising = self._get_star_rising_time()
        t_setting, y_setting = self._get_star_setting_time(t_rising)

        # If the first point is below the horizon, it indicates that this star doesn't rise
        if not y_rising and self._get_star_altaz(t_rising)[0].degrees < 0:
            raise ValueError(STAR_NEVER_RISES_MSG)

        ts, events = self._get_twilight_time(t_rising, t_setting)
        t_transit = self._get_star_meridian_transit_time(t_rising)

        # Set to 'none' to ensure the text is not converted to paths
        # plt.rcParams['svg.fonttype'] = 'none'

        # Set font
        # plt.rcParams['font.family'] = 'Arial'

        fig: Figure
        ax: PolarAxes
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})  # type: ignore
        ax.set_position((0.1, 0.1, 0.8, 0.8))
        ax.set_ylim(0, 90)
        ax.set_theta_offset(np.pi / 2)

        # Plot RTS & twilight transition points -----------------------|
        ttp_names: list[str]
        ttp_alts: list[np.float64]
        ttp_azs: list[np.float64]
        ttp_times: list[Time]
        rts_names: list[str]
        rts_alts: list[np.float64]
        rts_azs: list[np.float64]
        rts_times: list[Time]
        ttp_names, ttp_alts, ttp_azs, ttp_times = [], [], [], []
        rts_names, rts_alts, rts_azs, rts_times = [], [], [], []
        # Rises and sets
        if y_rising and y_setting:
            rts_names = ['R', 'T', 'S']
            rts_alts, rts_azs, rts_times = self._plot_rising_and_setting_points(
                fig, ax, t_rising, t_setting
            )
        # Circles
        else:
            rts_names = ['T']

        for i in range(len(ts) - 1):
            self._plot_in_style(ax, events[i], ts[i].ut1, ts[i + 1].ut1)
        if len(ts) > 2:
            ttp_names, ttp_alts, ttp_azs, ttp_times = (
                self._get_twilight_transition_points(ts, events)
            )
            self._plot_twilight_transition_points(fig, ax, ttp_alts, ttp_azs, ttp_names)

        mtp_alt, mtp_az = self._plot_meridian_transit_points(ax, t_transit)
        rts_alts.insert(1, mtp_alt)
        rts_azs.insert(1, mtp_az)
        rts_times.insert(1, t_transit)

        # Convert to a list. Each point is a tuple: (name, alt, az, time)
        points = list(zip(ttp_names, ttp_alts, ttp_azs, ttp_times)) + list(
            zip(rts_names, rts_alts, rts_azs, rts_times)
        )

        # Plot the poles ----------------------------------------------|
        self._plot_celestial_poles(ax)

        # Add tick labels ---------------------------------------------|
        r_ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        r_tick_labels = ['90°', '', '', '60°', '', '', '30°', '', '', '0°']
        # Skip the r=0 tick to avoid a redundant path in SVG
        ax.set_yticks(r_ticks[1:])
        ax.set_yticklabels([])

        for i in range(len(r_ticks)):
            ax.annotate(
                r_tick_labels[i],
                (np.pi, r_ticks[i]),
                textcoords="offset points",
                xytext=(3, 3),
                ha='left',
                va='bottom',
                fontsize=label_fontsize,
                color='gray',
            )
        ax.plot(0, 0, 'bo', ms=2, mec='b')
        ax.annotate(
            'Z',
            (0, 0),
            textcoords="offset points",
            xytext=(-3, 0),
            ha='right',
            va='center',
            fontsize=label_fontsize,
            color='b',
        )

        now = datetime.now()
        diagram_id = f"{now.timestamp():.3f}"  # unix timestamp -> str

        theta_ticks = [0, 90, 180, 270]
        theta_tick_labels = ['N\n(0°)', 'E\n(90°)', 'S\n(180°)', 'W\n(270°)']
        ax.set_thetagrids(angles=theta_ticks, labels=theta_tick_labels)
        ax.grid(color='gray', alpha=0.1)
        ax.tick_params(axis='x', pad=15, labelsize=label_fontsize)

        # Forces all text to be converted into graphical paths
        text: Text
        for text in ax.texts + ax.get_xticklabels():
            text.set_path_effects([path_effects.Normal()])

        # Image settings ----------------------------------------------|
        # Set the background color of the figure to transparent
        fig.patch.set_facecolor('none')
        fig.patch.set_alpha(0.0)

        # Set the background color of the polar plot to a light color
        ax.patch.set_facecolor('lavender')
        ax.patch.set_alpha(1.0)

        # Save SVG ----------------------------------------------------|
        # Save the diagram to an io.BytesIO object in SVG format
        svg_io = io.BytesIO()
        plt.savefig(svg_io, format='svg')
        plt.close()

        # Get the SVG data from the BytesIO object
        svg_data = svg_io.getvalue().decode('utf-8')
        # Replace 'standalone="no"' with 'standalone="yes"'
        svg_data = svg_data.replace('standalone="no"', 'standalone="yes"')
        # Remove the DOCTYPE declaration if present
        svg_data = re.sub(r'<!DOCTYPE svg .+?>', '', svg_data, flags=re.DOTALL)
        # Encode the SVG data to Base64
        svg_base64 = base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')

        return diagram_id, svg_base64, points

    def _get_annotations(
        self, points: list[tuple[str, np.float64, np.float64, Time]]
    ) -> Annotations:
        """Returns styled information of points."""
        # Sort the points by the UT1
        sorted_points = sorted(points, key=lambda p: p[3].ut1)

        annotations: Annotations = []
        for name, alt, az, t in sorted_points:
            _time_ut1 = t.ut1_calendar()
            _time_standard = ut1_to_standard_time(_time_ut1, self.offset_in_minutes)
            _time_local_mean = ut1_to_local_mean_time(_time_ut1, self.lng)
            _time_ut1 = timescale.ut1(
                *_time_ut1[:5], round(_time_ut1[5]) + 0.1
            ).ut1_calendar()
            _time_standard = timescale.ut1(
                *_time_standard[:5], round(_time_standard[5]) + 0.1
            ).ut1_calendar()
            _time_local_mean = timescale.ut1(
                *_time_local_mean[:5], round(_time_local_mean[5]) + 0.1
            ).ut1_calendar()
            _time_ut1_julian = juliandate.to_julian(
                juliandate.from_gregorian(*_time_ut1)
            )
            _time_standard_julian = juliandate.to_julian(
                juliandate.from_gregorian(*_time_standard)
            )
            _time_local_mean_julian = juliandate.to_julian(
                juliandate.from_gregorian(*_time_local_mean)
            )

            annotations.append(
                {
                    'name': name,
                    'is_displayed': True,
                    'alt': float(alt),
                    'az': float(az),
                    'time_ut1': tuple(map(int, _time_ut1)),
                    'time_standard': tuple(map(int, _time_standard)),
                    'time_local_mean': tuple(map(int, _time_local_mean)),
                    'time_ut1_julian': tuple(map(int, _time_ut1_julian[:6])),
                    'time_standard_julian': tuple(map(int, _time_standard_julian[:6])),
                    'time_local_mean_julian': tuple(
                        map(int, _time_local_mean_julian[:6])
                    ),
                    'time_zone': self.offset_in_minutes / 60,  # decimal hours
                }
            )

        return annotations


# ---------------------------------------------------------------------|
def get_diagram(
    year: int,
    month: int,
    day: int,
    lat: float,
    lng: float,
    tz_id: str,
    name: str | None = None,
    hip: int = -1,
    radec: tuple[float, float] | None = None,
) -> dict[str, str | float | Annotations]:
    """Entry point of getting the star path diagram.

    Returns:
        dict: A dict containing:
            {
                'diagram_id': str,
                'svg_data': str,
                'annotations': Annotations,
                'offset': float,
                'tz_name': str,
            }
    """
    star_obj = StarObject(
        year, month, day, lat=lat, lng=lng, tz_id=tz_id, name=name, hip=hip, radec=radec
    )

    # print(star_obj.year, star_obj.month, star_obj.day, star_obj.lat, star_obj.lng, star_obj.offset_in_minutes)
    # print(star_obj.tz_id, star_obj.offset_in_minutes, star_obj.name, star_obj.hip, star_obj.radec)

    result_dict = star_obj.generate_result()

    del star_obj

    return result_dict
