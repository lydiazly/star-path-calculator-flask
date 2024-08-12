# -*- coding: utf-8 -*-
# core/star_trail.py
"""
Functions to plot star trails.

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
from datetime import datetime
from skyfield.api import Star, wgs84, load
from skyfield.timelib import Time
from skyfield import almanac
import io
import base64
import re
import core.data_loader as dl
from utils.time_utils import get_standard_offset_by_id, ut1_to_local_standard_time
import juliandate

__all__ = ["get_star_trail_diagram", "get_annotations"]


tisca = load.timescale()
refraction_limit = -0.5666


# Ensure ephemeris data is loaded
if dl.eph is None or dl.earth is None:
    dl.load_data()
    # print("Warning: Ephemeris data was not loaded. `core.data_loader.load_data()` is called.")


def get_twilight_time(t: Time, lng: float, lat: float):
    t0 = t
    t1 = tisca.ut1_jd(t0.ut1 + 1)

    loc = wgs84.latlon(longitude_degrees=lng, latitude_degrees=lat)

    f = almanac.dark_twilight_day(dl.eph, loc)
    ts, events = almanac.find_discrete(t0, t1, f)
    # f returns a tuple of events when the time is:
    # 0 — Dark of night.
    # 1 — Astronomical twilight. (less than 18 degrees below the horizon)
    # 2 — Nautical twilight.  (less than 12 degrees below the horizon)
    # 3 — Civil twilight.  (less than 6 degrees below the horizon)
    # 4 — Sun is up.

    ts1 = []
    t_cals = ts.ut1_calendar()
    for i in range(len(ts)):
        t_cal = (t_cals[0][i], t_cals[1][i], t_cals[2][i],
                 t_cals[3][i], t_cals[4][i], t_cals[5][i])
        ts1.append(tisca.ut1(*t_cal))

    # add t0 before the beginning of the list and
    # add t1 behind the ending of the list
    ts1.insert(0, t0)
    # ts1.insert(len(ts1), t1)
    ts1.append(t1)
    events = list(events)
    events.insert(0, f(t0).item())
    # events.insert(len(events), f(t1).item())
    events.append(f(t1).item())

    return ts1, events


def get_star_altaz(s, t: Time, lng: float, lat: float):
    """
    Get the altazimuth coordinates of a star at a specific moment.
    The horizon angles are not considered.
    The atmospheric refraction is disregarded, neither.
    """

    loc = wgs84.latlon(longitude_degrees=lng, latitude_degrees=lat)
    observer = dl.earth + loc
    alt, az, dist = observer.at(t).observe(s).apparent().altaz()

    return (alt, az)


def get_star_rising_time(s, t: Time, lng: float, lat: float, offset_in_minutes: float):
    """
    The star rising time is also the starting of the 1-day period for calculation.
    """

    year, month, day, _, _, _ = t.ut1_calendar()

    t0 = tisca.ut1(year, month, day, 0, 0 - offset_in_minutes, 0)
    t1 = tisca.ut1(year, month, day + 1, 0, 0 - offset_in_minutes, 0)

    loc = wgs84.latlon(longitude_degrees=lng, latitude_degrees=lat)
    observer = dl.earth + loc

    t_risings, y_risings = almanac.find_risings(observer, s, t0, t1)

    return t_risings, y_risings


def get_star_setting_time(s, t: Time, lng: float, lat: float):
    """
    Search for the star setting time during this 1-day period since star rising.
    """

    t0 = t
    t1 = tisca.ut1_jd(t0.ut1 + 1)

    loc = wgs84.latlon(longitude_degrees=lng, latitude_degrees=lat)
    observer = dl.earth + loc

    t_settings, y_settings = almanac.find_settings(observer, s, t0, t1)

    return t_settings, y_settings


def get_star_meridian_transit_time(s, t: Time, lng: float, lat: float):

    t0 = t
    t1 = tisca.ut1_jd(t0.ut1 + 1)

    loc = wgs84.latlon(longitude_degrees=lng, latitude_degrees=lat)
    observer = dl.earth + loc

    t_transits = almanac.find_transits(observer, s, t0, t1)

    return t_transits


def plot_in_style(ax, event, t_jd0, t_jd1, s, lng: float, lat: float):
    """
    Plot star trails in different styles for different twilight conditions.
    t0 and t1 are both in units of Julian days.
    """

    pts_num = int((t_jd1 - t_jd0) * 100)
    t_jds = np.linspace(t_jd0, t_jd1, pts_num if pts_num>10 else 10)

    altitudes = np.zeros(shape=(0), dtype=float)
    azimuths = np.zeros(shape=(0), dtype=float)
    for ti in t_jds:
        alt, az = get_star_altaz(s, tisca.ut1_jd(ti), lng, lat)
        altitudes = np.append(altitudes, [alt.degrees])
        azimuths = np.append(azimuths, [az.degrees])

    r = 90 - altitudes
    theta = np.radians(azimuths)
    
    # Get rid of the points that are close to the antipode of the zenith.
    mask = r < 150
    
    if event == 0 or event == 1:
        line, = ax.plot(theta[mask], r[mask], 'k-', lw=2)
    if event == 2:
        line, = ax.plot(theta[mask], r[mask], 'k--', lw=2)
        line.set_dashes([2,2])
    if event == 3:
        line, = ax.plot(theta[mask], r[mask], 'k--', lw=2, alpha=0.4)
        line.set_dashes([2,2])
    if event == 4:
        line, = ax.plot(theta[mask], r[mask], 'k--', lw=0.5)
        line.set_dashes([1,4])


def get_twilight_transition_points(ts, events, s, lng: float, lat: float):
    """
    Find transition points between different twilight conditions.
    """

    altitudes = []
    azimuths = []
    annotations = []
    pts = []

    for i in range(1, len(ts)-1):
        alt, az = get_star_altaz(s, ts[i], lng, lat)

        if events[i-1] == 4 and events[i] == 3 and alt.degrees>refraction_limit:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('N1')
            pts.append(ts[i])
        if events[i-1] == 3 and events[i] == 2 and alt.degrees>refraction_limit:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('N2')
            pts.append(ts[i])
        if events[i-1] == 2 and events[i] == 1 and alt.degrees>refraction_limit:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('N3')
            pts.append(ts[i])
        if events[i-1] == 1 and events[i] == 2 and alt.degrees>refraction_limit:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('D1')
            pts.append(ts[i])
        if events[i-1] == 2 and events[i] == 3 and alt.degrees>refraction_limit:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('D2')
            pts.append(ts[i])
        if events[i-1] == 3 and events[i] == 4 and alt.degrees>refraction_limit:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('D3')
            pts.append(ts[i])

    return altitudes, azimuths, annotations, pts


def plot_meridian_transit_points(ax, t, s, lng: float, lat: float):
    """
    Find meridian transit points (once in a day).
    """

    alt, az = get_star_altaz(s, t, lng, lat)

    r = 90 - alt.degrees
    theta = np.radians(az.degrees)

    ax.plot(theta, r, 'ro', ms=6)
    if lat >= 0:
        ax.annotate('T', (theta, r), textcoords="offset points", xytext=(0, 15), ha='center',va='top',
                    fontsize=10, color='r')
    else:
        ax.annotate('T', (theta, r), textcoords="offset points", xytext=(0, -15), ha='center',va='top',
                    fontsize=10, color='r')

    return alt.degrees, az.degrees


def plot_twilight_transition_points(fig, ax, altitudes, azimuths, annotations, lng, lat):
    """
    Plot the twilight transition points as well as their labels.
    """

    r = 90 - np.array(altitudes)
    theta = np.radians(azimuths)

    for i, j, k in zip(theta, r, annotations):
        ax.plot(i, j, 'ro', ms=4)

    # The code below is in order to draw the labels of twilight transition points with adjust_text
    # temparorily keep it
    # texts = []
    # for i, j, k in zip(theta, r, annotations):
    #     ax.plot(i, j, 'ro', ms=4)
    #     texts.append(plt.text(i, j, k, ha='center', va='center', color='r'))
    # adjust_text(texts, x=theta_interp, y=r_interp, expand=(2,2), force_static=(1,1), min_arrow_len=10,
    #             arrowprops=dict(arrowstyle="->", color='r', lw=1, shrinkA=0, shrinkB=2, mutation_scale=10))

    # Draw the labels of twilight transition points
    ttp_coord_bg = []
    for i in range(len(r)):
        _coord = ax.transData.transform((theta[i], r[i]))
        ttp_coord_bg.append([_coord[0]/fig.bbox.width, _coord[1]/fig.bbox.height])
    if lat >= 0:
        _coord = ax.transData.transform((0, 90-lat))
        cp_coord_bg = [_coord[0]/fig.bbox.width, _coord[1]/fig.bbox.height]
    else:
        _coord = ax.transData.transform((np.radians(180), 90+lat))
        cp_coord_bg = [_coord[0]/fig.bbox.width, _coord[1]/fig.bbox.height]

    ax2 = fig.add_axes([0,0,1,1], facecolor=(1,1,1,0))
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

    _vector = np.array(ttp_coord_bg[0]) - np.array(cp_coord_bg)
    _vector_length = np.sqrt(np.sum(_vector**2))
    if _vector_length < 0.1:
        _offset_scale = 0.05
        _flag = 1
    else:
        _offset_scale = 0.02
        _flag = 0

    for i in range(len(ttp_coord_bg)):
        _vector = np.array(ttp_coord_bg[i]) - np.array(cp_coord_bg)
        _vector_length = np.sqrt(np.sum(_vector**2))
        _unit_vector = _vector / _vector_length
        _offset = _unit_vector * _offset_scale

        if _flag == 1:
            ax2.annotate(annotations[i],
                xy = (ttp_coord_bg[i][0], ttp_coord_bg[i][1]),
                xytext = (ttp_coord_bg[i][0] + _offset[0], ttp_coord_bg[i][1] + _offset[1]),
                arrowprops=dict(color='r', arrowstyle='-', shrinkA=0.2, shrinkB=0.2, lw=0.5),
                va='center', ha='center', fontsize=10, color='r')
        else:
            ax2.annotate(annotations[i],
                xy = (ttp_coord_bg[i][0], ttp_coord_bg[i][1]),
                xytext = (ttp_coord_bg[i][0] + _offset[0], ttp_coord_bg[i][1] + _offset[1]),
                va='center', ha='center', fontsize=10, color='r')

    ax2.axis('off')


def plot_rising_and_setting_points(fig, ax, t0, t1, s, lng:float, lat:float):
    """
    Plot the star rising and setting points, whose latitudes are both at the refraction limit.
    They are outside the plotting range, so they are both plotted on the ax2 layer
    which is above the ax layer where the star trails are drawn on.
    """

    alt0, az0 = get_star_altaz(s, t0, lng, lat)
    alt1, az1 = get_star_altaz(s, t1, lng, lat)

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
    ax2.annotate('R', (x0, y0), textcoords="offset points", xytext=(-10, 0), ha='right',
                  va='center', fontsize=10, color='r')
    ax2.plot(x1, y1, 'ro', ms=6)
    ax2.annotate('S', (x1, y1), textcoords="offset points", xytext=(10, 0), ha='left',
                     va='center', fontsize=10, color='r')
    ax2.axis('off')

    return [alt0.degrees, alt1.degrees], [az0.degrees, az1.degrees], [t0, t1]


def plot_celestial_poles(ax, lat):
    """
    Plot the north celestial pole or the south celestial pole.
    """

    if lat>0:
        r = 90 - lat
        theta = 0
        ax.plot(theta, r, 'b+', ms=8)
        ax.annotate('NCP', (theta, r), textcoords="offset points", xytext=(-6, 0), ha='right', va='center', fontsize=10, color='b')
    elif lat<0:
        r = 90 + lat
        theta = np.radians(180)
        ax.plot(theta, r, 'b+', ms=8)
        ax.annotate('SCP', (theta, r), textcoords="offset points", xytext=(-6, 0), ha='right', va='center', fontsize=10, color='b')


def get_star_trail_diagram(t: Time, lng: float, lat: float, offset_in_minutes: float,
                           name=None, hip: int = -1, radec: Tuple[float, float] = None):
    s = None
    if name is not None:
        if name in ['mercury', 'venus', 'mars']:
            s = dl.eph[name]
        elif name in ['jupiter', 'saturn', 'uranus', 'neptune', 'pluto']:
            s = dl.eph[name + ' barycenter']
        else:
            raise ValueError(f"Invalid planet name: {name}")
    elif hip >= 0:
        if hip < 1 or hip > 118322:
            raise ValueError("The Hipparchus Catalogue Number must be in the range [1, 118322].")
        try:
            s = Star.from_dataframe(dl.hip_df.loc[hip])
        except KeyError:
            raise ValueError("Invalid Hipparchus Catalogue Number.")
    elif radec and len(radec) == 2:
        s = Star(ra_hours=float(radec[0]), dec_degrees=float(radec[1]))

    if not s:
        raise ValueError("Invalid celestial object.")

    t_risings, y_risings = get_star_rising_time(s, t, lng, lat, offset_in_minutes)
    t_starting = t_risings[0]
    t_settings, y_settings = get_star_setting_time(s, t_starting, lng, lat)
    ts, events = get_twilight_time(t_starting, lng, lat)
    t_transits = get_star_meridian_transit_time(s, t_starting, lng, lat)

    t_jds = np.array([t.ut1 for t in ts])

    # Insert the setting point to the array representing twilight transition points
    t_jd_setting = t_settings[0].ut1
    ind_tst = np.sum(t_jds < t_jd_setting)
    ts_combined = np.insert(t_jds, ind_tst, t_jd_setting)
    events_combined = np.insert(events, ind_tst, events[ind_tst-1])

    # Adjusting Matplotlib rcParams to ensure text is not converted to paths
    plt.rcParams['svg.fonttype'] = 'none'
    # plt.rcParams['font.family'] = 'Arial'

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    ax.set_position([0.1, 0.1, 0.8, 0.8])
    ax.set_ylim(0, 90)
    ax.set_theta_offset(np.pi/2)

    for i in range(len(ts_combined)-1):
        plot_in_style(ax, events_combined[i], ts_combined[i], ts_combined[i+1], s, lng, lat)

    ttp_alt, ttp_az, ttp_anno, ttp_ts = get_twilight_transition_points(ts, events, s, lng, lat)
    plot_twilight_transition_points(fig, ax, ttp_alt, ttp_az, ttp_anno, lng, lat)
    plot_celestial_poles(ax, lat)

    if y_risings[0] and y_settings[0]:
        rts_alt, rts_az, rts_ts = plot_rising_and_setting_points(fig, ax, t_risings[0], t_settings[0], s, lng, lat)
        mtp_alt, mtp_az = plot_meridian_transit_points(ax, t_transits[0], s, lng, lat)
        rts_alt.insert(1, mtp_alt)
        rts_az.insert(1, mtp_az)
        rts_ts.insert(1, t_transits[0])
    elif not y_risings[0] and get_star_altaz(s, t_risings[0], lng, lat)[0].degrees < refraction_limit:
        rts_alt, rts_az, rts_ts = [], [], []
        raise ValueError('This star never rises on this day.')
    else:
        mtp_alt, mtp_az = plot_meridian_transit_points(ax, t_transits[0], s, lng, lat)
        rts_alt = [mtp_alt]
        rts_az = [mtp_az]
        rts_ts = [t_transits[0]]

    r_ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    r_tick_labels = ['90°', '', '', '60°', '', '', '30°', '', '', '0°']
    ax.set_yticks(r_ticks)
    ax.set_yticklabels([])

    for i in range(len(r_ticks)):
        ax.annotate(r_tick_labels[i], (np.pi, r_ticks[i]), textcoords="offset points", xytext=(3, 3),
                    ha='left', va='bottom', fontsize=10, color='gray')
    ax.plot(0, 0, 'bo', ms=2, mec='b')
    ax.annotate('Z', (0, 0), textcoords="offset points", xytext=(-3, 0), ha='right', va='center', fontsize=10, color='b')

    now = datetime.now()
    diagram_id = f"{now.timestamp():.3f}"  # unix timestamp -> str

    ax.set_thetagrids(angles=[0, 90, 180, 270], labels=['N\n(0°)', 'E\n(90°)', 'S\n(180°)', 'W\n(270°)'])
    ax.grid(color='gray', alpha=0.1)
    ax.tick_params(axis='x', pad=15, labelsize=10)

    # Set the background color of the figure to transparent
    fig.patch.set_facecolor('none')
    fig.patch.set_alpha(0.0)

    # Set the background color of the polar plot to a light color
    ax.patch.set_facecolor('lavender')
    ax.patch.set_alpha(1.0)

    # Save the diagram as an SVG to an io.BytesIO object
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

    return diagram_id, svg_base64, (ttp_alt, ttp_az, ttp_anno, ttp_ts), (rts_alt, rts_az, rts_ts)


def get_annotations(ttp, rts, offset_in_minutes: float):

    ttp_alt, ttp_az, ttp_anno, ttp_times = ttp
    rts_alt, rts_az, rts_times = rts

    name_list = ['D1', 'D2', 'D3', 'N1', 'N2', 'N3', 'R', 'T', 'S']
    annotations = [{
        'name': i,
        'is_displayed': False,
        'alt': None,
        'az': None,
        'time_ut1': None,
        'time_local': None,
        'time_zone': None,
        'time_ut1_julian': None,
        'time_local_julian': None
    } for i in name_list]

    for i in range(len(ttp_anno)):
        ind = name_list.index(ttp_anno[i])
        _time_ut1 = ttp_times[i].ut1_calendar()
        _time_local = ut1_to_local_standard_time(_time_ut1, offset_in_minutes)
        _time_ut1_julian   = juliandate.to_julian(juliandate.from_gregorian(*_time_ut1))
        _time_local_julian = juliandate.to_julian(juliandate.from_gregorian(*_time_local))
        annotations[ind]['is_displayed'] = True
        annotations[ind]['alt'] = float(ttp_alt[i])
        annotations[ind]['az']  = float(ttp_az[i])
        annotations[ind]['time_ut1']          = (*map(int, _time_ut1[:5]), float(_time_ut1[-1]))
        annotations[ind]['time_ut1_julian']   = (*map(int, _time_ut1_julian[:5]), float(_time_ut1_julian[-2]+_time_ut1_julian[-1]/1e6))
        annotations[ind]['time_local']        = (*map(int, _time_local[:5]), float(_time_local[-1]))
        annotations[ind]['time_local_julian'] = (*map(int, _time_local_julian[:5]), float(_time_local_julian[-2]+_time_local_julian[-1]/1e6))
        annotations[ind]['time_zone'] = offset_in_minutes / 60

    if len(rts_alt) > 1:
        for i, name in enumerate(['R', 'T', 'S']):
            ind = name_list.index(name)
            _time_ut1 = rts_times[i].ut1_calendar()
            _time_local = ut1_to_local_standard_time(_time_ut1, offset_in_minutes)
            _time_ut1_julian   = juliandate.to_julian(juliandate.from_gregorian(*_time_ut1))
            _time_local_julian = juliandate.to_julian(juliandate.from_gregorian(*_time_local))
            annotations[ind]['is_displayed'] = True
            annotations[ind]['alt'] = float(rts_alt[i])
            annotations[ind]['az']  = float(rts_az[i])
            annotations[ind]['time_ut1']          = (*map(int, _time_ut1[:5]), float(_time_ut1[-1]))
            annotations[ind]['time_ut1_julian']   = (*map(int, _time_ut1_julian[:5]), float(_time_ut1_julian[-2]+_time_ut1_julian[-1]/1e6))
            annotations[ind]['time_local']        = (*map(int, _time_local[:5]), float(_time_local[-1]))
            annotations[ind]['time_local_julian'] = (*map(int, _time_local_julian[:5]), float(_time_local_julian[-2]+_time_local_julian[-1]/1e6))
            annotations[ind]['time_zone'] = offset_in_minutes / 60
    elif len(rts_alt) == 1:
        ind = name_list.index('T')
        _time_ut1 = rts_times[0].ut1_calendar()
        _time_local = ut1_to_local_standard_time(_time_ut1, offset_in_minutes)
        _time_ut1_julian   = juliandate.to_julian(juliandate.from_gregorian(*_time_ut1))
        _time_local_julian = juliandate.to_julian(juliandate.from_gregorian(*_time_local))
        annotations[ind]['is_displayed'] = True
        annotations[ind]['alt'] = float(rts_alt[0])
        annotations[ind]['az'] = float(rts_az[0])
        annotations[ind]['time_ut1']          = (*map(int, _time_ut1[:5]), float(_time_ut1[-1]))
        annotations[ind]['time_ut1_julian']   = (*map(int, _time_ut1_julian[:5]), float(_time_ut1_julian[-2]+_time_ut1_julian[-1]/1e6))
        annotations[ind]['time_local']        = (*map(int, _time_local[:5]), float(_time_local[-1]))
        annotations[ind]['time_local_julian'] = (*map(int, _time_local_julian[:5]), float(_time_local_julian[-2]+_time_local_julian[-1]/1e6))
        annotations[ind]['time_zone'] = offset_in_minutes / 60

    return annotations

def get_diagram(year: int, month: int, day: int, lat: float, lng: float, tz_id: str,
                name=None, hip: int = -1, radec: Tuple[float, float] = None) -> dict:
    t1 = tisca.ut1(year, month, day)

    offset_in_minutes = get_standard_offset_by_id(tz_id)

    diagram_id, svg_data, ttp, rts = get_star_trail_diagram(t=t1, lng=lng, lat=lat, offset_in_minutes=offset_in_minutes,
                                                            name=name, hip=hip, radec=radec)

    annotations = get_annotations(ttp=ttp, rts=rts, offset_in_minutes=offset_in_minutes)

    return {
      "diagram_id": diagram_id,
      "svg_data": svg_data,
      "annotations": annotations,
      "offset": offset_in_minutes,
    }
