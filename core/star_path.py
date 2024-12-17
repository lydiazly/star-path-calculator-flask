# -*- coding: utf-8 -*-
# core/star_path.py
"""
Functions to plot star paths.

Use global variables eph and earth by referencing, e.g.:
```
import core.data_loader as dl
some_value = dl.eph.some_method()
```
"""

import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-interactive plotting

from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from datetime import datetime
from skyfield.api import Star, wgs84, load
from skyfield.timelib import Time
from skyfield import almanac
import io
import base64
import re
import core.data_loader as dl
from utils.time_utils import get_standard_offset_by_id, ut1_to_standard_time, ut1_to_local_mean_time
import juliandate
from great_circle_calculator.great_circle_calculator import distance_between_points, intermediate_point

__all__ = ["get_diagram"]


tisca = load.timescale()

# Manually set the atmospheric refractive angle at the horizon to 34.476 arcminutes
horizon_degree = -0.5666 - 0.008

label_fontsize = 10

# Ensure ephemeris data is loaded
if dl.eph is None or dl.earth is None:
    dl.load_data()
    # print("Warning: Ephemeris data was not loaded. `core.data_loader.load_data()` is called.")


#------------------------------------------------------------------------------|
class StarObject:
    def __init__(self, year: int, month: int, day: int, lat: float, lng: float, tz_id: str,
                 name=None, hip: int = -1, radec: Tuple[float, float] = None):
        self.year = year
        self.month = month
        self.day = day
        self.lat = lat
        self.lng = lng
        self.tz_id = tz_id
        self.name = name
        self.hip = hip
        self.radec = radec

        self.offset_in_minutes = get_standard_offset_by_id(tz_id)
        self._t = tisca.ut1(year, month, day, 0, 0 - self.offset_in_minutes, 0)  # standard time at 0:00:00
        self.star = self._initialize_star()


    def _initialize_star(self):
        s = None
        if self.name is not None:
            if self.name in ['mercury', 'venus', 'mars']:
                s = dl.eph[self.name]
            elif self.name in ['jupiter', 'saturn', 'uranus', 'neptune', 'pluto']:
                s = dl.eph[self.name + ' barycenter']
            else:
                raise ValueError(f"Invalid planet name: {self.name}")
        elif self.hip >= 0:
            if self.hip < 1 or self.hip > 118322:
                raise ValueError("The Hipparcos Catalogue number must be in the range [1, 118322].")
            try:
                _s = dl.hip_df.loc[self.hip]
                if np.isnan(_s['ra_degrees']):
                    raise ValueError("WARNING: No RA/Dec data available for this star in the Hipparcos Catalogue.")
                s = Star.from_dataframe(_s)
            except KeyError:
                raise ValueError("WARNING: Entry not found in Hipparcos Catalogue.")
        elif self.radec and len(self.radec) == 2:
            # The unit of RA is converted from degrees to hours
            s = Star(ra_hours=float(self.radec[0]/360*24), dec_degrees=float(self.radec[1]))

        if not s:
            raise ValueError("Invalid celestial object.")

        return s


    def generate_result(self):
        diagram_id, svg_data, ttp, rts = self._get_star_path_diagram()
        annotations = self._get_annotations(ttp, rts)
        return {
            "diagram_id": diagram_id,
            "svg_data": svg_data,
            "annotations": annotations,
            "offset": self.offset_in_minutes,
        }


    def _get_twilight_time(self, t0: Time, t1: Time):
        """
        Gets twilight transition times.
        """

        loc = wgs84.latlon(longitude_degrees=self.lng, latitude_degrees=self.lat)

        f = almanac.dark_twilight_day(dl.eph, loc)
        ts, events = almanac.find_discrete(t0, t1, f)
        # f returns a tuple of events when the time is:
        # 0 — Dark of night
        # 1 — Astronomical twilight (less than 18 degrees below the horizon)
        # 2 — Nautical twilight (less than 12 degrees below the horizon)
        # 3 — Civil twilight (less than 6 degrees below the horizon)
        # 4 — Sun is up

        if len(ts) == 0:
            ts1 = []
            ts1.append(t0)
            ts1.append(t1)
            events = list(events)
            events.append(f(t0).item())
            events.append(f(t1).item())

            return ts1, events

        else:
            ts1 = []
            t_cals = ts.ut1_calendar()
            for i in range(len(ts)):
                t_cal = (t_cals[0][i], t_cals[1][i], t_cals[2][i],
                         t_cals[3][i], t_cals[4][i], t_cals[5][i])
                ts1.append(tisca.ut1(*t_cal))

            # Add t0 before the beginning of the list
            # Add t1 behind the ending of the list
            ts1.insert(0, t0)
            ts1.append(t1)
            events = list(events)
            events.insert(0, f(t0).item())
            events.append(f(t1).item())

            return ts1, events


    def _get_star_altaz(self, t: Time):
        """
        Gets the altazimuth coordinates of a star at a specific moment.
        The horizon angles are not considered.
        The atmospheric refraction is included by setting parameter `temperature_C` to 'standard' (10 degree Celsius).
        """

        loc = wgs84.latlon(longitude_degrees=self.lng, latitude_degrees=self.lat)
        observer = dl.earth + loc
        alt, az, dist = observer.at(t).observe(self.star).apparent().altaz(temperature_C='standard')

        return (alt, az)


    def _get_star_rising_time(self):
        """
        Gets the star's rising time. The star path is calculated from this moment.
        """

        t0 = self._t
        # t1 = tisca.ut1(self.year, self.month, self.day + 3, 0, 0 - self.offset_in_minutes, 0)
        t1 = tisca.ut1_jd(t0.ut1 + 3)

        loc = wgs84.latlon(longitude_degrees=self.lng, latitude_degrees=self.lat)
        observer = dl.earth + loc

        t_risings, y_risings = almanac.find_risings(observer, self.star, t0, t1, horizon_degrees=horizon_degree)

        return t_risings[0], y_risings[0]


    def _get_star_setting_time(self, t_rising: Time):
        """
        Gets the star's setting time. The star path's calculation ends at this moment.
        """

        t0 = self._t
        t1 = tisca.ut1_jd(t0.ut1 + 3)

        loc = wgs84.latlon(longitude_degrees=self.lng, latitude_degrees=self.lat)
        observer = dl.earth + loc

        t_settings, y_settings = almanac.find_settings(observer, self.star, t0, t1, horizon_degrees=horizon_degree)
        for i, ti in zip(range(len(t_settings)), t_settings):
            if ti.ut1 - t_rising.ut1 > 1e-6:
                break

        return t_settings[i], y_settings[i]


    def _get_star_meridian_transit_time(self, t_rising: Time):
        """
        Gets the star's meridian transit time.
        """

        t0 = t_rising
        t1 = tisca.ut1_jd(t0.ut1 + 2)

        loc = wgs84.latlon(longitude_degrees=self.lng, latitude_degrees=self.lat)
        observer = dl.earth + loc

        t_transits = almanac.find_transits(observer, self.star, t0, t1)

        return t_transits[0]


    def _plot_in_style(self, ax, event, t_jd0, t_jd1):
        """
        Plots the star path in different styles for different twilight stages.
        Input times are in units of Julian days.
        """

        pts_num = int((t_jd1 - t_jd0) * 100)
        t_jds = np.linspace(t_jd0, t_jd1, pts_num if pts_num > 10 else 10)

        altitudes = np.zeros(shape=(0), dtype=float)
        azimuths = np.zeros(shape=(0), dtype=float)
        for ti in t_jds:
            alt, az = self._get_star_altaz(tisca.ut1_jd(ti))
            altitudes = np.append(altitudes, [alt.degrees])
            azimuths = np.append(azimuths, [az.degrees])

        r = 90 - altitudes
        theta = np.radians(azimuths)

        if event == 0 or event == 1:
            line, = ax.plot(theta, r, 'k-', lw=2)
        elif event == 2:
            line, = ax.plot(theta, r, 'k--', lw=2)
            line.set_dashes([2,2])
        elif event == 3:
            line, = ax.plot(theta, r, 'k--', lw=2, alpha=0.4)
            line.set_dashes([2,2])
        elif event == 4:
            line, = ax.plot(theta, r, 'k--', lw=0.5)
            line.set_dashes([1,4])


    def _get_twilight_transition_points(self, ts, events):
        """
        Gets transition points between different twilight conditions.
        """

        altitudes = []
        azimuths = []
        names = []
        times = []

        for i in range(1, len(ts)-1):
            alt, az = self._get_star_altaz(ts[i])

            if events[i-1] == 4 and events[i] == 3:
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                names.append('N1')
                times.append(ts[i])
            if events[i-1] == 3 and events[i] == 2:
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                names.append('N2')
                times.append(ts[i])
            if events[i-1] == 2 and events[i] == 1:
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                names.append('N3')
                times.append(ts[i])
            if events[i-1] == 1 and events[i] == 2:
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                names.append('D1')
                times.append(ts[i])
            if events[i-1] == 2 and events[i] == 3:
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                names.append('D2')
                times.append(ts[i])
            if events[i-1] == 3 and events[i] == 4:
                altitudes.append(alt.degrees)
                azimuths.append(az.degrees)
                names.append('D3')
                times.append(ts[i])

        return altitudes, azimuths, names, times


    def _plot_meridian_transit_points(self, ax, t_transit: Time):
        """
        Gets meridian transit points (once in a day).
        """

        alt, az = self._get_star_altaz(t_transit)

        r = 90 - alt.degrees
        theta = np.radians(az.degrees)

        ax.plot(theta, r, 'ro', ms=6)
        if self.lat >= 0:
            ax.annotate('T', (theta, r), textcoords="offset points", xytext=(0, 15),
                        ha='center',va='top', fontsize=label_fontsize, color='r')
        else:
            ax.annotate('T', (theta, r), textcoords="offset points", xytext=(0, -16),
                        ha='center',va='bottom', fontsize=label_fontsize, color='r')

        return alt.degrees, az.degrees


    def _plot_twilight_transition_points(self, fig, ax, altitudes, azimuths, names):
        """
        Plots twilight transition points as well as their labels.
        """

        if len(altitudes) == 0:
            return

        r = 90 - np.array(altitudes)
        theta = np.radians(azimuths)

        for i, j, k in zip(theta, r, names):
            ax.plot(i, j, 'ro', ms=4)

        # The code below is to temporarily draw the labels of twilight transition points with adjust_text:
        # texts = []
        # for i, j, k in zip(theta, r, names):
        #     ax.plot(i, j, 'ro', ms=4)
        #     texts.append(plt.text(i, j, k, ha='center', va='center', color='r'))
        # adjust_text(texts, x=theta_interp, y=r_interp, expand=(2,2), force_static=(1,1), min_arrow_len=10,
        #             arrowprops=dict(arrowstyle="->", color='r', lw=1, shrinkA=0, shrinkB=2, mutation_scale=10))

        # Draw the labels of twilight transition points.
        # Label positions are set at the points on the extended segments of the great circles
        # connecting from the pole to the twilight transition points.
        # The reat_circle_calculator package is used to take calculation for great circles.
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

            _vector_length = distance_between_points(cp_coord, _ttp_coord, unit='meters', haversine=True)
            if _vector_length < 2.2e6 and i == 0:
                _offset_scale = 1.5 * 1e6
            _label_coord = intermediate_point(cp_coord, _ttp_coord, 1 + _offset_scale / _vector_length)

            if _label_coord[0] < 0:
                _label_coord = (_label_coord[0] + 360, _label_coord[1])

            label_coord.append(_label_coord)

        ax2 = fig.add_axes([0,0,1,1], facecolor=(1,1,1,0))
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)

        for i in range(len(label_coord)):
            _r = 90 - label_coord[i][1]
            _theta = np.radians(label_coord[i][0])
            label_coord_bg = ax.transData.transform((_theta, _r))
            label_coord_bg = [label_coord_bg[0]/fig.bbox.width, label_coord_bg[1]/fig.bbox.height]

            ttp_coord_bg = ax.transData.transform((theta[i], r[i]))
            ttp_coord_bg = ([ttp_coord_bg[0]/fig.bbox.width, ttp_coord_bg[1]/fig.bbox.height])

            ax2.annotate(names[i],
                         xy = (ttp_coord_bg[0], ttp_coord_bg[1]),
                         xytext = (label_coord_bg[0], label_coord_bg[1]),
                         arrowprops=dict(color='r', arrowstyle='-', shrinkA=0.2, shrinkB=0.2, lw=0.5),
                         va='center', ha='center', fontsize=label_fontsize, color='r')

        ax2.axis('off')


    def _plot_rising_and_setting_points(self, fig, ax, t0, t1):
        """
        Plots the star's rising and setting points, whose latitudes are both at the refraction limit.
        Because their coordinates are out of the plotting range, they are plotted on the ax2 layer.
        The ax2 layer is above the ax layer, where the star paths are drawn on.
        """

        alt0, az0 = self._get_star_altaz(t0)
        alt1, az1 = self._get_star_altaz(t1)

        r0 = 90 - alt0.degrees
        theta0 = np.radians(az0.degrees)
        r1 = 90 - alt1.degrees
        theta1 = np.radians(az1.degrees)

        # Get the coordinates of the points on fig layer, which are originally drawn on the ax layer.
        # Deliver the obtained coordinates to ax2 layer by dividing them with fig's width and height.
        pcoord0 = ax.transData.transform((theta0, r0))
        x0 = pcoord0[0]/fig.bbox.width
        y0 = pcoord0[1]/fig.bbox.height
        pcoord1 = ax.transData.transform((theta1, r1))
        x1 = pcoord1[0]/fig.bbox.width
        y1 = pcoord1[1]/fig.bbox.height

        ax2 = fig.add_axes([0,0,1,1], facecolor=(1,1,1,0))
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)

        ax2.plot(x0, y0, 'ro', ms=6)
        ax2.annotate('R', (x0, y0), textcoords="offset points", xytext=(-10, 0),
                     ha='right', va='center', fontsize=label_fontsize, color='r')
        ax2.plot(x1, y1, 'ro', ms=6)
        ax2.annotate('S', (x1, y1), textcoords="offset points", xytext=(10, 0),
                     ha='left', va='center', fontsize=label_fontsize, color='r')
        ax2.axis('off')

        return [alt0.degrees, alt1.degrees], [az0.degrees, az1.degrees], [t0, t1]


    def _plot_celestial_poles(self, ax):
        """
        Plots the north/south celestial pole.
        """

        if self.lat > 0:
            r = 90 - self.lat
            theta = 0
            ax.plot(theta, r, 'b+', ms=8)
            ax.annotate('NCP', (theta, r), textcoords="offset points", xytext=(-6, 0),
                        ha='right', va='center', fontsize=label_fontsize, color='b')
        elif self.lat < 0:
            r = 90 + self.lat
            theta = np.radians(180)
            ax.plot(theta, r, 'b+', ms=8)
            ax.annotate('SCP', (theta, r), textcoords="offset points", xytext=(-6, 0),
                        ha='right', va='center', fontsize=label_fontsize, color='b')


    def _get_star_path_diagram(self):
        """
        Plots the star path.
        """

        t_rising, y_rising = self._get_star_rising_time()
        t_setting, y_setting = self._get_star_setting_time(t_rising)
        ts, events = self._get_twilight_time(t_rising, t_setting)
        t_transit = self._get_star_meridian_transit_time(t_rising)

        # Set to 'none' to ensure the text is not converted to paths
        # plt.rcParams['svg.fonttype'] = 'none'

        # Set font
        # plt.rcParams['font.family'] = 'Arial'

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
        ax.set_position([0.1, 0.1, 0.8, 0.8])
        ax.set_ylim(0, 90)
        ax.set_theta_offset(np.pi/2)

        if y_rising and y_setting:
            for i in range(len(ts)-1):
                self._plot_in_style(ax, events[i], ts[i].ut1, ts[i+1].ut1)
            if len(ts) > 2:
                ttp_alt, ttp_az, ttp_name, ttp_time = self._get_twilight_transition_points(ts, events)
                self._plot_twilight_transition_points(fig, ax, ttp_alt, ttp_az, ttp_name)
            else:
                ttp_alt, ttp_az, ttp_name, ttp_time = [], [], [], []
            self._plot_celestial_poles(ax)
            rts_alt, rts_az, rts_time = self._plot_rising_and_setting_points(fig, ax, t_rising, t_setting)
            mtp_alt, mtp_az = self._plot_meridian_transit_points(ax, t_transit)
            rts_alt.insert(1, mtp_alt)
            rts_az.insert(1, mtp_az)
            rts_time.insert(1, t_transit)

        elif not y_rising and self._get_star_altaz(t_rising)[0].degrees < 0:
            ttp_alt, ttp_az, ttp_name, ttp_time = [], [], [], []
            rts_alt, rts_az, rts_time = [], [], []
            raise ValueError('WARNING: This star never rises at this location on this date.')

        else:
            for i in range(len(ts)-1):
                self._plot_in_style(ax, events[i], ts[i].ut1, ts[i+1].ut1)
            if len(ts) > 2:
                ttp_alt, ttp_az, ttp_name, ttp_time = self._get_twilight_transition_points(ts, events)
                self._plot_twilight_transition_points(fig, ax, ttp_alt, ttp_az, ttp_name)
            else:
                ttp_alt, ttp_az, ttp_name, ttp_time = [], [], [], []
            self._plot_celestial_poles(ax)
            mtp_alt, mtp_az = self._plot_meridian_transit_points(ax, t_transit)
            rts_alt = [mtp_alt]
            rts_az = [mtp_az]
            rts_time = [t_transit]

        r_ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        r_tick_labels = ['90°', '', '', '60°', '', '', '30°', '', '', '0°']
        ax.set_yticks(r_ticks)
        ax.set_yticklabels([])

        for i in range(len(r_ticks)):
            ax.annotate(r_tick_labels[i], (np.pi, r_ticks[i]), textcoords="offset points", xytext=(3, 3),
                        ha='left', va='bottom', fontsize=label_fontsize, color='gray')
        ax.plot(0, 0, 'bo', ms=2, mec='b')
        ax.annotate('Z', (0, 0), textcoords="offset points", xytext=(-3, 0),
                    ha='right', va='center', fontsize=label_fontsize, color='b')

        now = datetime.now()
        diagram_id = f"{now.timestamp():.3f}"  # unix timestamp -> str

        theta_ticks = [0, 90, 180, 270]
        theta_tick_labels = ['N\n(0°)', 'E\n(90°)', 'S\n(180°)', 'W\n(270°)']
        ax.set_thetagrids(angles=theta_ticks, labels=theta_tick_labels)
        ax.grid(color='gray', alpha=0.1)
        ax.tick_params(axis='x', pad=15, labelsize=label_fontsize)

        # Forces all text to be converted into graphical paths without any distortion or special effects
        [text.set_path_effects([path_effects.Normal()]) for text in (ax.texts + ax.get_xticklabels())]

        # Set the background color of the figure to transparent
        fig.patch.set_facecolor('none')
        fig.patch.set_alpha(0.0)

        # Set the background color of the polar plot to a light color
        ax.patch.set_facecolor('lavender')
        ax.patch.set_alpha(1.0)

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

        return diagram_id, svg_base64, (ttp_alt, ttp_az, ttp_name, ttp_time), (rts_alt, rts_az, rts_time)


    def _set_annotation_values(self, annotations, ind, t, alt, az):
        """
        Helper function to set up the annotations.
        """
        _time_ut1        = t.ut1_calendar()
        _time_standard   = ut1_to_standard_time(_time_ut1, self.offset_in_minutes)
        _time_local_mean = ut1_to_local_mean_time(_time_ut1, self.lng)
        _time_ut1        = tisca.ut1(*_time_ut1[:5], round(_time_ut1[5]) + 0.1).ut1_calendar()
        _time_standard   = tisca.ut1(*_time_standard[:5], round(_time_standard[5]) + 0.1).ut1_calendar()
        _time_local_mean = tisca.ut1(*_time_local_mean[:5], round(_time_local_mean[5]) + 0.1).ut1_calendar()
        _time_ut1_julian        = juliandate.to_julian(juliandate.from_gregorian(*_time_ut1))
        _time_standard_julian   = juliandate.to_julian(juliandate.from_gregorian(*_time_standard))
        _time_local_mean_julian = juliandate.to_julian(juliandate.from_gregorian(*_time_local_mean))
        annotations[ind]['is_displayed'] = True
        annotations[ind]['alt'] = float(alt)
        annotations[ind]['az']  = float(az)
        annotations[ind]['time_ut1']               = tuple(map(int, _time_ut1))
        annotations[ind]['time_ut1_julian']        = tuple(map(int, _time_ut1_julian[:6]))
        annotations[ind]['time_standard']          = tuple(map(int, _time_standard))
        annotations[ind]['time_standard_julian']   = tuple(map(int, _time_standard_julian[:6]))
        annotations[ind]['time_local_mean']        = tuple(map(int, _time_local_mean))
        annotations[ind]['time_local_mean_julian'] = tuple(map(int, _time_local_mean_julian[:6]))
        annotations[ind]['time_zone'] = self.offset_in_minutes / 60


    def _get_annotations(self, ttp, rts):
        """
        Returns styled information of points.
        """

        ttp_alts, ttp_azs, ttp_names, ttp_times = ttp
        rts_alts, rts_azs, rts_times = rts

        name_list = ['D1', 'D2', 'D3', 'N1', 'N2', 'N3', 'R', 'T', 'S']
        annotations = [{
            'name': i,
            'is_displayed': False,
            'alt': None,
            'az': None,
            'time_ut1': None,
            'time_standard': None,
            'time_local_mean': None,
            'time_zone': None,
            'time_ut1_julian': None,
            'time_standard_julian': None,
            'time_local_mean_julian': None
        } for i in name_list]

        for i in range(len(ttp_names)):
            ind = name_list.index(ttp_names[i])
            self._set_annotation_values(annotations, ind, ttp_times[i], ttp_alts[i], ttp_azs[i])

        if len(rts_alts) > 1:
            for i, name in enumerate(['R', 'T', 'S']):
                ind = name_list.index(name)
                self._set_annotation_values(annotations, ind, rts_times[i], rts_alts[i], rts_azs[i])

        elif len(rts_alts) == 1:
            ind = name_list.index('T')
            self._set_annotation_values(annotations, ind, rts_times[0], rts_alts[0], rts_azs[0])

        return annotations


#------------------------------------------------------------------------------|
def get_diagram(year: int, month: int, day: int, lat: float, lng: float, tz_id: str,
                name=None, hip: int = -1, radec: Tuple[float, float] = None) -> dict:
    """
    Entry point of getting the star path diagram.
    """

    star_obj = StarObject(year, month, day, lat, lng, tz_id, name, hip, radec)

    # print(star_obj.year, star_obj.month, star_obj.day, star_obj.lat, star_obj.lng, star_obj.offset_in_minutes)
    # print(star_obj.tz_id, star_obj.offset_in_minutes, star_obj.name, star_obj.hip, star_obj.radec)

    result_dict = star_obj.generate_result()

    del star_obj

    return result_dict
