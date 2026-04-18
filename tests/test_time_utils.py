# -*- coding: utf-8 -*-
# tests/test_time_utils.py
import pytest
from core.data_loader import timescale
from utils.time_utils import (
    get_tzid_by_tzfpy,
    get_standard_offset_by_id,
    ut1_to_standard_time,
    ut1_to_local_mean_time,
    gregorian_to_julian,
    julian_to_gregorian,
    get_cc_date,
)


@pytest.mark.parametrize(
    "lat, lng, tz_expected",
    [
        (0, 0, 'Etc/GMT'),  # GMT
        (40, -180, 'Etc/GMT+12'),  # Etc/GMT±12
        (40, 180, 'Etc/GMT-12'),  # Etc/GMT±12
        (40, -179.9999, 'Etc/GMT+12'),  # Etc/GMT+12
        (47.650499, -122.350070, 'America/Los_Angeles'),  # Los Angeles
        (49.3, -123.1, 'America/Vancouver'),  # Vancouver
        (43.839319, 87.526148, 'Asia/Shanghai'),  # Ürümqi
        (47.8, 88.1, 'Asia/Shanghai'),  # Altay
        (22.598127, 120.347287, "Asia/Taipei"),  # Taipei
        (53.3, -110.0, 'America/Edmonton'),  # Lloydminster, Alberta
        (-33.8698439, 151.2082848, 'Australia/Sydney'),  # Sydney
        # (45.036933, 12.826174, 'Asia/Riyadh'),  # 'Europe/Rome' (incorrect) Aden International Airport
        (91, 0, ''),  # Invalid
        (0, 181, ''),  # Invalid
    ],
)
def test_timezone(lat, lng, tz_expected):
    """Tests the time zone ID finder."""
    assert get_tzid_by_tzfpy(lat, lng) == tz_expected


@pytest.mark.parametrize(
    "tz_id, offset_in_hours_expected, tzname_expected",
    [
        ('Europe/London', '0.0', 'GMT'),
        ('America/Vancouver', '-8.0', 'PST'),
        ('Asia/Shanghai', '8.0', 'CST'),
        ('Asia/Urumqi', '6.0', '+06'),
        ('America/New_York', '-5.0', 'EST'),
        ('Australia/Sydney', '10.0', 'AEST'),
    ],
)
def test_standard_offset(tz_id, offset_in_hours_expected, tzname_expected):
    """Tests getting the Standard Time offset."""
    offset_in_minutes, tz_name = get_standard_offset_by_id(tz_id)
    assert f'{offset_in_minutes / 60:.1f}' == offset_in_hours_expected
    assert tz_name == tzname_expected


test_times = [
    ((2000, 1, 1, 12, 0, 0), -8, -120, (2000, 1, 1, 4, 0, 0)),
    ((2000, 1, 1, 12, 0, 0), -7.5, -112.5, (2000, 1, 1, 4, 30, 0)),
    ((2000, 1, 1, 12, 0, 0), 5.5, 82.5, (2000, 1, 1, 17, 30, 0)),
]


@pytest.mark.parametrize("t_ut1, offset_in_hours, _, t_standard_expected", test_times)
def test_ut1_to_standard_time(t_ut1, offset_in_hours, _, t_standard_expected):
    """Tests UT1 to standard time conversion."""
    t = ut1_to_standard_time(t_ut1, offset_in_hours * 60)
    assert (
        tuple(map(int, timescale.ut1(*t[:5], round(t[5]) + 0.1).ut1_calendar()))
        == t_standard_expected
    )


@pytest.mark.parametrize("t_ut1, _, lng, t_standard_expected", test_times)
def test_ut1_to_local_mean_time(t_ut1, _, lng, t_standard_expected):
    """Tests UT1 to LMT conversion."""
    t = ut1_to_local_mean_time(t_ut1, lng)
    assert (
        tuple(map(int, timescale.ut1(*t[:5], round(t[5]) + 0.1).ut1_calendar()))
        == t_standard_expected
    )


# https://en.wikipedia.org/wiki/Conversion_between_Julian_and_Gregorian_calendars
# https://ytliu0.github.io/ChineseCalendar/index_simp.html
test_dates = [
    ((-722, 12, 23), (-722, 12, 31), None, None),
    (
        (-722, 12, 24),
        (-721, 1, 1),
        # '鲁惠公四十六年 (戊午) 十二月十六 (丙寅日)',
        '戊午年十二月十六',
        '戊午年十二月十六',
    ),
    (
        (445, 2, 26),
        (445, 2, 25),
        # '宋文帝元嘉二十二年 (乙酉) 二月初三 (己卯月·癸亥日)',
        '乙酉年二月初三',
        '乙酉年二月初三',
    ),
    (
        (1582, 10, 15),
        (1582, 10, 5),
        # '明神宗万历十年 (壬午) 九月十九 (庚戌月·甲戌日)',
        '壬午年九月十九',
        '壬午年九月十九',
    ),
    (
        (1582, 10, 14),
        (1582, 10, 4),
        # '明神宗万历十年 (壬午) 九月十八 (庚戌月·癸酉日)',
        '壬午年九月十八',
        '壬午年九月十八',
    ),
    (
        (2100, 3, 14),
        (2100, 2, 29),
        # '庚申年二月初四 (己卯月·乙卯日)',
        '庚申年二月初四',
        '庚申年二月初四',
    ),
    ((2201, 1, 1), (2200, 12, 17), None, None),
]


@pytest.mark.parametrize("date_g, date_j, date_hans, date_hant", test_dates)
def test_get_cc_date(date_g, date_j, date_hans, date_hant):
    """Tests the conversion among Gregorian, Julian, and Chinese calendars."""
    assert gregorian_to_julian((*date_g, 12))[:3] == date_j
    assert julian_to_gregorian((*date_j, 12))[:3] == date_g
    res = get_cc_date(date_g, date_j)
    assert (None if res[0] is None else res[0]['formatted']) == date_hans
    assert (None if res[1] is None else res[1]['formatted']) == date_hant
