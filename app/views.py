# app/views.py
from flask import request, jsonify, render_template, current_app as app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from core.coordinates import get_coords
from core.star_trail import get_diagram

# Initialize the limiter
limiter = Limiter(
    get_remote_address,
    default_limits=["720 per hour", "60 per minute"],
    storage_uri="memory://",
    strategy="fixed-window"
)


def init_limiter(app):
    limiter.init_app(app)


@app.errorhandler(429)
def ratelimit_error(e):
    return jsonify({"error": f"For security, we rate-limit requests as: {str(e.description)}. Please try again later."}), 429


@app.route("/equinox", methods=["GET"])
@limiter.limit("4/second", override_defaults=False)
def equinox():
    year   = request.args.get("year", default=None, type=int)
    # month  = request.args.get("month", default=1, type=int)
    # day    = request.args.get("day", default=1, type=int)
    # hour   = request.args.get("hour", default=12, type=int)
    # minute = request.args.get("minute", default=0, type=int)
    # second = request.args.get("second", default=0, type=float)

    if year is None:
        return jsonify({"error": "The year must be provided."}), 400

    try:
        # results = get_coords(year, month, day, hour, minute, second)
        results = get_coords(year)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "year":    str(year),
        # "month":   str(month),
        # "day":     str(day),
        # "hour":    str(hour),
        # "minute":  str(minute),
        # "second":  str(second),
        "results": results,
    }), 200


@app.route("/diagram", methods=["GET"])
@limiter.limit("4/second", override_defaults=False)
def diagram():
    year  = request.args.get("year", default=None, type=int)
    month = request.args.get("month", default=1, type=int)
    day   = request.args.get("day", default=1, type=int)
    lat   = request.args.get("lat", default=None, type=float)
    lng   = request.args.get("lng", default=None, type=float)
    flag  = request.args.get("flag", default=None)
    name  = request.args.get("name", default=None)
    hip   = request.args.get("hip", default=-1, type=int)
    ra    = request.args.get("ra", default=None, type=float)
    dec   = request.args.get("dec", default=None, type=float)

    if year is None:
        return jsonify({"error": "The year must be provided."}), 400

    if lat is None or lng is None:
        return jsonify({"error": "The longitude and latitude must be provided."}), 400

    if name:
        obj = {"name": name.lower()}
    elif hip > 0:
        obj = {"hip": hip}
    elif ra is not None and dec is not None:
        obj = {"radec": (ra, dec)}
    else:
        return jsonify({"error": "Either planet name, Hipparchus catalogue number, or (ra, dec) must be provided."}), 400

    # TODO: test equinox/solstice times
    eqx_sol_keys = {
        "ve": "vernal_time",
        "ss": "summer_time",
        "ae": "autumnal_time",
        "ws": "winter_time"
    }
    eqx_sol_time = []
    if flag in eqx_sol_keys:
        eqx_sol_time = get_coords(year)[eqx_sol_keys[flag]]  # [int, int, int, int, int, float]
        month = eqx_sol_time[1]
        day = eqx_sol_time[2]

    try:
        results = get_diagram(year, month, day, lat=lat, lng=lng, **obj)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "year":        str(year),
        "month":       str(month),
        "day":         str(day),
        "flag":        flag,
        "lat":         str(lat),
        "lng":         str(lng),
        "name":        name,
        "hip":         hip,
        "ra":          ra,
        "dec":         dec,
        "diagramId":   str(results["diagram_id"]),
        "svgData":     results["svg_data"],
        "annotations": results["annotations"],
        "eqxSolTime":  eqx_sol_time
    }), 200


@app.route("/")
@limiter.limit("5/second", override_defaults=False)
def home():
    return render_template("index.html")
