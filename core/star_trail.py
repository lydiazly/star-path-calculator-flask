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
from skyfield.api import N, Star, W, wgs84, load, Timescale
from skyfield import almanac
from adjustText import adjust_text
import io
import base64
import re
import core.data_loader as dl
from utils.time_utils import get_standard_offset, ut1_to_local_standard_time

__all__ = ["get_star_trail_diagram", "get_annotations"]


# TODO: use a global ts
# ts = load.timescale()


if dl.eph is None:
    dl.load_data()
    # print("Warning: Ephemeris data was not loaded. `core.data_loader.load_data()` is called.")


def get_twilight_time(starting_ts: Timescale, lng: float, lat: float):
    ts = load.timescale()
    t0 = starting_ts
    t1 = ts.ut1_jd(t0.ut1 + 1)
    
    loc = wgs84.latlon(longitude_degrees=lng, latitude_degrees=lat)
    
    f = almanac.dark_twilight_day(dl.eph, loc)
    times, events = almanac.find_discrete(t0, t1, f)
    # f returns a tuple of events when the time is:
    # 0 — Dark of night.
    # 1 — Astronomical twilight. (less than 18 degrees below the horizon)
    # 2 — Nautical twilight.  (less than 12 degrees below the horizon)
    # 3 — Civil twilight.  (less than 6 degrees below the horizon)
    # 4 — Sun is up.
    
    times_ut1 = []
    times_temp = times.ut1_calendar()
    for i in range(len(times)):
        times_tuple = (times_temp[0][i], times_temp[1][i], times_temp[2][i], 
                       times_temp[3][i], times_temp[4][i], times_temp[5][i])
        times_ut1.append(ts.ut1(*times_tuple))
    
    # add t0 before the beginning of the list and
    # add t1 behind the ending of the list
    times_ut1.insert(0, t0)
    times_ut1.insert(len(times_ut1), t1)
    events = list(events)
    events.insert(0, f(t0).item())
    events.insert(len(events), f(t1).item())
        
    return times_ut1, events


def get_star_altaz(s, ts: Timescale, lng: float, lat: float):
    """
    Get the altazimuth coordinates of a star at a specific moment.
    The horizon angles are not considered.
    The atmospheric refraction is disregarded, neither.
    """

    loc = wgs84.latlon(longitude_degrees=lng, latitude_degrees=lat)
    observer = dl.earth + loc
    alt, az, dist = observer.at(ts).observe(s).apparent().altaz()
    
    return (alt, az)


def get_star_rising_time(s, ts: Timescale, lng: float, lat: float):
    """
    The star rising time is also the starting of the 1-day period for calculation.
    """
    
    year, month, day, _, _, _ = ts.ut1_calendar()
    
    offset_in_minutes = get_standard_offset(lng, lat)
    tst = load.timescale()
    t0 = tst.ut1(year, month, day, 0, 0-offset_in_minutes, 0)
    t1 = tst.ut1(year, month, day+1, 0, 0-offset_in_minutes, 0)
    
    loc = wgs84.latlon(longitude_degrees=lng, latitude_degrees=lat)
    observer = dl.earth + loc
    
    t_risings, y_risings = almanac.find_risings(observer, s, t0, t1)
    
    return t_risings, y_risings


def get_star_setting_time(s, starting_ts: Timescale, lng: float, lat: float):
    """
    Search for the star setting time during this 1-day period since star rising.
    """
    
    ts = load.timescale()
    t0 = starting_ts
    t1 = ts.ut1_jd(starting_ts.ut1 + 1)
    
    loc = wgs84.latlon(longitude_degrees=lng, latitude_degrees=lat)
    observer = dl.earth + loc
    
    t_settings, y_settings = almanac.find_settings(observer, s, t0, t1)
    
    return t_settings, y_settings


def plot_in_style(ax, event, t0, t1, s, lng: float, lat: float):
    """
    Plot star trails in different styles for different twilight conditions.
    t0 and t1 are both in units of Julian days.
    """
    
    ts = load.timescale()
    t = np.linspace(t0, t1, 100)
    altitudes = np.zeros(shape=(0), dtype=float)
    azimuths = np.zeros(shape=(0), dtype=float)
    for ti in t:
        alt, az = get_star_altaz(s, ts.ut1_jd(ti), lng, lat)
        altitudes = np.append(altitudes, [alt.degrees])
        azimuths = np.append(azimuths, [az.degrees])
    
    r = 90 - altitudes
    theta = np.radians(azimuths)
    
    if event == 0 or event == 1:
        line, = ax.plot(theta, r, 'k-', lw=2)
    if event == 2:
        line, = ax.plot(theta, r, 'k--', lw=2)
        line.set_dashes([5,3])
    if event == 3:
        line, = ax.plot(theta, r, 'k--', lw=1.5, alpha=0.3)
        line.set_dashes([5,3])
    if event == 4:
        line, = ax.plot(theta, r, 'k--', lw=0.5)
        line.set_dashes([1,4])


def get_twilight_transition_points(times, events, s, lng: float, lat: float):
    """
    Find transition points between different twilight conditions.
    """
    
    altitudes = []
    azimuths = []
    annotations = []
    ptimes = []
    for i in range(1, len(times)-1):
        alt, az = get_star_altaz(s, times[i], lng, lat)
        
        if events[i-1] == 4 and events[i] == 3 and alt.degrees>-0.5666:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('N1')
            ptimes.append(times[i])
        if events[i-1] == 3 and events[i] == 2 and alt.degrees>-0.5666:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('N2')
            ptimes.append(times[i])
        if events[i-1] == 2 and events[i] == 1 and alt.degrees>-0.5666:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('N3')
            ptimes.append(times[i])
        if events[i-1] == 1 and events[i] == 2 and alt.degrees>-0.5666:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('D1')
            ptimes.append(times[i])
        if events[i-1] == 2 and events[i] == 3 and alt.degrees>-0.5666:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('D2')
            ptimes.append(times[i])
        if events[i-1] == 3 and events[i] == 4 and alt.degrees>-0.5666:
            altitudes.append(alt.degrees)
            azimuths.append(az.degrees)
            annotations.append('D3')
            ptimes.append(times[i])

    return altitudes, azimuths, annotations, ptimes


def plot_twilight_transition_points(ax, altitudes, azimuths, annotations, t_interp, s, lng: float, lat: float):
    """
    Plot the twilight transition points as well as their labels.
    """
    
    ts = load.timescale()
    alt_interp = []
    az_interp = []
    for i in range(len(t_interp)):
        alt, az = get_star_altaz(s, ts.ut1_jd(t_interp[i]), lng, lat)
        alt_interp.append(alt.degrees)
        az_interp.append(az.degrees)
    
    r = 90 - np.array(altitudes)
    theta = np.radians(azimuths)
    r_interp = 90 - np.array(alt_interp)
    theta_interp =  np.radians(az_interp)
    
    texts = []
    for i, j, k in zip(theta, r, annotations):
        ax.plot(i, j, 'ro', ms=6)
        texts.append(plt.text(i, j, k, ha='center', va='center'))
    adjust_text(texts, x=theta_interp, y=r_interp, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))
    # try:
    #     ax.annotate(annotations, (theta, r), textcoords="offset points", xytext=(0, -10), ha='center',va='top',
    #                 fontsize=10, color='r')
    # except:
    #     pass


def plot_rising_and_setting_points(fig, ax, t0, t1, s, lng:float, lat:float):
    """
    Plot the star rising and setting points.
    They are outside the plotting range, so they are both plotted on the ax2 layer 
    which is above the ax layer where the star trails are drawn on.
    """
    
    ts = load.timescale()
    alt0, az0 = get_star_altaz(s, ts.ut1_jd(t0), lng, lat)
    alt1, az1 = get_star_altaz(s, ts.ut1_jd(t1), lng, lat)
    
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
    ax2.annotate('RISING\nPOINT', (x0, y0), textcoords="offset points", xytext=(-20, 0), ha='right', 
                  va='center', fontsize=10, color='r')
    ax2.plot(x1, y1, 'ro', ms=6)
    ax2.annotate('SETTING\nPOINT', (x1, y1), textcoords="offset points", xytext=(20, 0), ha='left', 
                     va='center', fontsize=10, color='r')
    
    return [alt0.degrees, alt1.degrees], [az0.degrees, az1.degrees], [ts.ut1_jd(t0), ts.ut1_jd(t1)]


def get_star_trail_diagram(ts: Timescale, lng: float, lat: float,
                           planet = None, hip: int = -1, radec: Tuple[float, float] = None):
    s = None
    if planet is not None:
        # TODO: check planet string
        s = dl.eph[str(planet)]
    elif hip > 0:
        # TODO: handel Hipparchus (remove `pass` after complete)
        # s = ...
        pass
    elif radec is not None and len(radec) == 2:
        s = Star(ra_hours=float(radec[0]), dec_degrees=float(radec[1]))
    
    if s is None:
        raise ValueError("Either planet, Hipparchus, or (ra, dec) is invalid.")
    
    t_risings, y_risings = get_star_rising_time(s, ts, lng, lat)
    starting_ts = t_risings[0]
    t_settings, y_settings = get_star_setting_time(s, starting_ts, lng, lat)
    times, events = get_twilight_time(starting_ts, lng, lat)
    
    times_jd = np.array([t.ut1 for t in times])
    
    tst = t_settings[0].ut1
    ind_tst = len(times_jd[(times_jd - tst) < 0])
    times_combined = np.insert(times_jd, ind_tst, tst)
    events_combined = np.insert(events, ind_tst, events[ind_tst-1])
    
    # Adjusting Matplotlib rcParams to ensure text is not converted to paths
    plt.rcParams['svg.fonttype'] = 'none'
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    ax.set_ylim(0, 90)
    ax.set_theta_offset(np.pi/2)
    for i in range(len(times_combined)-1):
        plot_in_style(ax, events_combined[i], times_combined[i], times_combined[i+1], s, lng, lat)
    ttp_alt, ttp_az, ttp_anno, ttp_times = get_twilight_transition_points(times, events, s, lng, lat)
    t_interp = np.linspace(times[0].ut1, times[-1].ut1, 1000)
    plot_twilight_transition_points(ax, ttp_alt, ttp_az, ttp_anno, t_interp, s, lng, lat)
    
    if y_risings[0] and y_settings[0]:
        rsp_alt, rsp_az, rsp_times = plot_rising_and_setting_points(fig, ax, starting_ts.ut1, tst, s, lng, lat)
    elif not y_risings[0] and get_star_altaz(s, starting_ts, lng, lat)[0].degrees<-0.5666:
        rsp_alt = []
        rsp_az = []
        rsp_times = []
        raise ValueError('This star never rises on this day.')
    else:
        rsp_alt = []
        rsp_az = []
        rsp_times = []
    
    r_ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    r_tick_labels=['90°', '', '', '60°', '', '', '30°', '', '', '0°']
    ax.set_yticks(r_ticks)
    ax.set_yticklabels([])
    
    for i in range(len(r_ticks)):
        ax.annotate(str(r_tick_labels[i]), (np.pi, r_ticks[i]), textcoords="offset points", xytext=(3, 3),
                    ha='left', va='bottom', fontsize=10, color='gray')
    
    now = datetime.now()
    diagram_id = f"{now.timestamp():.3f}"  # unix timestamp -> str

    ax.set_thetagrids(angles=[0, 90, 180, 270], labels=['N', 'E', 'S', 'W'])
    ax.grid(color='gray', alpha=0.1)

    # Set the background color of the figure to transparent
    fig.patch.set_facecolor('none')
    fig.patch.set_alpha(0.0)

    # Set the background color of the polar plot to light gray
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
    
    return diagram_id, svg_base64, (ttp_alt, ttp_az, ttp_anno, ttp_times), (rsp_alt, rsp_az, rsp_times)


def get_annotations(ttp, rsp, lng:float, lat:float):
    
    ttp_alt, ttp_az, ttp_anno, ttp_times = ttp
    rsp_alt, rsp_az, rsp_times = rsp
    
    name_list = ['D1', 'D2', 'D3', 'N1', 'N2', 'N3', 'R', 'S']
    annotations = []
    for i in name_list:
        z = {}
        z['name'] = i
        z['is_displayed'] = False
        z['alt'] = None
        z['az'] = None
        z['time_ut1'] = None
        z['time_local'] = None
        z['time_zone'] = None
        annotations.append(z)
    
    for i in range(len(ttp_anno)):
        ind = np.where(np.array(name_list) == ttp_anno[i])[0][0]
        _time_ut1 = ttp_times[i].ut1_calendar()
        _time_local = ut1_to_local_standard_time(ttp_times[i].ut1_calendar(), lng, lat)
        annotations[ind]['is_displayed'] = True
        annotations[ind]['alt'] = float(ttp_alt[i])
        annotations[ind]['az'] = float(ttp_az[i])
        annotations[ind]['time_ut1'] = (*map(int, _time_ut1[0:5]), float(_time_ut1[-1]))
        annotations[ind]['time_local'] = (*map(int, _time_local[0:5]), float(_time_local[-1]))
        annotations[ind]['time_zone'] = get_standard_offset(lng, lat) / 60
    
    _anno = ['R', 'S']
    if len(rsp_alt) > 0:
        for i in range(len(_anno)):
            ind = np.where(np.array(name_list) == _anno[i])[0][0]
            annotations[ind]['is_displayed'] = True
            annotations[ind]['alt'] = rsp_alt[i]
            annotations[ind]['az'] = rsp_az[i]
            annotations[ind]['time_ut1'] = rsp_times[i].ut1_calendar()
            annotations[ind]['time_local'] = ut1_to_local_standard_time(rsp_times[i].ut1_calendar(), lng, lat)
            annotations[ind]['time_zone'] = get_standard_offset(lng, lat) / 60
    
    return annotations

def get_diagram(year: int, month: int, day: int, lat: float, lng: float,
                planet = None, hip: int = -1, radec: Tuple[float, float] = None) -> dict:
    ts = load.timescale()
    ts1 = ts.ut1(year, month, day)
    # print([year, month, day, hour, lat, lng])

    diagram_id, svg_data, ttp, rsp = get_star_trail_diagram(ts=ts1, lng=lng, lat=lat,
                                                                 planet=planet, hip=hip, radec=radec)
    
    annotations = get_annotations(ttp=ttp, rsp=rsp, lng=lng, lat=lat)

    return {
      "diagram_id": diagram_id,
      "svg_data": svg_data,
      "annotations": annotations,
    }
