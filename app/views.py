# app/views.py
from flask import request, jsonify, render_template, current_app as app
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
from core.coordinates import get_seasons
from core.star_path import get_diagram
from utils.time_utils import get_standard_offset_by_id, ut1_to_local_standard_time, julian_to_gregorian, gregorian_to_julian


EQX_SOL_KEYS = {
    "ve": "vernal_time",
    "ss": "summer_time",
    "ae": "autumnal_time",
    "ws": "winter_time"
}

GREGORIAN = ""
JULIAN = "j"

# Initialize the limiter
# limiter = Limiter(
#     get_remote_address,
#     default_limits=["720 per hour", "60 per minute"],
#     storage_uri="memory://",
#     strategy="fixed-window"
# )


# def init_limiter(app):
#     limiter.init_app(app)


# @app.errorhandler(429)
# def ratelimit_error(e):
#     return jsonify({"error": f"For security, we rate-limit requests as: {str(e.description)}. Please try again later."}), 429


@app.route("/seasons", methods=["GET"])
# @limiter.limit("6/second", override_defaults=False)
def seasons():
    # [Gregorian]
    from core.coordinates import get_coords

    lat   = request.args.get("lat", default=None, type=float)
    lng   = request.args.get("lng", default=None, type=float)
    tz_id = request.args.get("tz", default=None)
    year  = request.args.get("year", default=None, type=int)

    if year is None:
        return jsonify({"error": "Year is not provided."}), 400

    try:
        if not tz_id:
            if lat is None or lng is None:
                return jsonify({"error": "Either longitude or latitude is not provided."}), 400
            from utils.time_utils import find_timezone
            tz_id = find_timezone(lat=lat, lng=lng)

        offset_in_minutes = get_standard_offset_by_id(tz_id)
        results = get_coords(year)  # coordinates & times

        # Convert from UT1 to Standard Time
        for key in EQX_SOL_KEYS.values():
            t_local = ut1_to_local_standard_time(results[key], offset_in_minutes=offset_in_minutes)
            results[key] = (*map(int, t_local[0:5]), float(t_local[-1]))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "tz":      tz_id,
        "year":    year,  # keep as a number
        "results": results,  # keep the elements as numbers
    }), 200


@app.route("/equinox", methods=["GET"])
# @limiter.limit("6/second", override_defaults=False)
def equinox():
    # [Gregorian]
    lat   = request.args.get("lat", default=None, type=float)
    lng   = request.args.get("lng", default=None, type=float)
    tz_id = request.args.get("tz", default=None)
    year  = request.args.get("year", default=None, type=int)
    flag  = request.args.get("flag", default=None)

    if year is None:
        return jsonify({"error": "Year is not provided."}), 400

    if flag is None or flag not in EQX_SOL_KEYS:
        return jsonify({"error": "Equinox or solstice not specified or invalid."}), 400

    try:
        if not tz_id:
            if lat is None or lng is None:
                return jsonify({"error": "Either longitude or latitude is not provided."}), 400
            from utils.time_utils import find_timezone
            tz_id = find_timezone(lat=lat, lng=lng)

        offset_in_minutes = get_standard_offset_by_id(tz_id)
        results = get_seasons(year)[EQX_SOL_KEYS[flag]]  # time, keep the elements as numbers: (int, int, int, int, int, float)

        # Convert from UT1 to Standard Time
        t_local = ut1_to_local_standard_time(results, offset_in_minutes=offset_in_minutes)
        results = (*map(int, t_local[0:5]), float(t_local[-1]))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "tz":      tz_id,
        "year":    year,  # keep as a number
        "results": results,  # keep the elements as numbers
    }), 200


@app.route("/diagram", methods=["GET"])
# @limiter.limit("4/second", override_defaults=False)
def diagram():
    lat   = request.args.get("lat", default=None, type=float)
    lng   = request.args.get("lng", default=None, type=float)
    tz_id = request.args.get("tz", default=None)
    year  = request.args.get("year", default=None, type=int)
    month = request.args.get("month", default=1, type=int)
    day   = request.args.get("day", default=1, type=int)
    flag  = request.args.get("flag", default=None)  # unused
    cal   = request.args.get("cal", default=None)  # None: Gregorian, "j": Julian
    name  = request.args.get("name", default=None)
    hip   = request.args.get("hip", default=None, type=int)
    ra    = request.args.get("ra", default=None, type=float)
    dec   = request.args.get("dec", default=None, type=float)

    if lat is None or lng is None:
        return jsonify({"error": "Either longitude or latitude is not provided."}), 400

    if year is None:
        return jsonify({"error": "Year is not provided."}), 400

    if name:
        obj = {"name": name.lower()}
    elif hip is not None:
        obj = {"hip": hip}
        # from utils.star_utils import hip_to_name
        # name = hip_to_name(hip)
    elif ra is not None and dec is not None:
        obj = {"radec": (ra, dec)}
    else:
        return jsonify({"error": "Either planet name, Hipparchus Catalogue number, or (ra, dec) is not provided."}), 400

    # Convert to Gregorian if the request is in Julian
    if cal == JULIAN:
        year, month, day, *_ = julian_to_gregorian((year, month, day, 12))  # 12:00:00

    # Get the equinox/solstice times
    # eqx_sol_time = []
    # if flag is not None:
    #     if flag in EQX_SOL_KEYS:
    #         eqx_sol_time = get_coords(year)[EQX_SOL_KEYS[flag]]  # keep the elements as numbers: (int, int, int, int, int, float)
    #         month = eqx_sol_time[1]
    #         day = eqx_sol_time[2]

    try:
        if not tz_id:
            from utils.time_utils import find_timezone
            tz_id = find_timezone(lat=lat, lng=lng)

        results = get_diagram(year, month, day, lat=lat, lng=lng, tz_id=tz_id, **obj)

        if cal == JULIAN:
            # The results are already in Gregorian
            cal = GREGORIAN
        else:
            # Convert to Julian if the original request was in Gregorian
            year, month, day, *_ = gregorian_to_julian((year, month, day, 12))  # 12:00:00
            cal = JULIAN
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "lat":         lat,  # keep as a number
        "lng":         lng,  # keep as a number
        "tz":          tz_id,
        "offset":      results["offset"] / 60,  # decimal hours, keep as a number
        "year":        year,  # in the other calendar, keep as a number
        "month":       month,  # in the other calendar, keep as a number
        "day":         day,  # in the other calendar, keep as a number
        "flag":        flag,
        "cal":         cal,  # the other calendar
        "name":        name,
        "hip":         str(hip) if hip else None,
        "ra":          ra,  # keep as a number
        "dec":         dec,  # keep as a number
        "diagramId":   str(results["diagram_id"]),
        "svgData":     results["svg_data"],
        "annotations": results["annotations"],
        "eqxSolTime":  []  # unused
    }), 200


@app.route("/")
# @limiter.limit("5/second", override_defaults=False)
def home():
    return render_template("index.html")
