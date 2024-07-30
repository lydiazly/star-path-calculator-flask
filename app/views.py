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
def coords():
    year   = request.args.get("year")
    # month  = request.args.get("month", default=1, type=int)
    # day    = request.args.get("day", default=1, type=int)
    # hour   = request.args.get("hour", default=12, type=int)
    # minute = request.args.get("minute", default=0, type=int)
    # second = request.args.get("second", default=0, type=float)

    if year is None:
        return jsonify({"error": "Year is required."}), 400

    try:
        year   = int(year)
        # month  = int(month)
        # day    = int(day)
        # hour   = int(hour)
        # minute = int(minute)
        # second = float(second)
    except ValueError:
        return jsonify({"error": "The year must be an integers."}), 400

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
    year  = request.args.get("year")
    month = request.args.get("month", default=1, type=int)
    day   = request.args.get("day", default=1, type=int)
    lat   = request.args.get("lat", default=50, type=float)
    lng   = request.args.get("lng", default=-140, type=float)
    flag  = request.args.get("flag")
    name  = request.args.get("name")
    hip   = request.args.get("hip", default=-1, type=int)
    ra    = request.args.get("ra")
    dec   = request.args.get("dec")

    try:
        year  = int(year)
        month = int(month)
        day   = int(day)
    except ValueError:
        return jsonify({"error": "Date must be integers."}), 400
    
    try:
        lat   = float(lat)
        lng   = float(lng)
    except ValueError:
        return jsonify({"error": "Longitude and latitude must be floats."}), 400

    if (name):
        obj = {"name": str(name).lower()}
    elif (hip > 0):
        obj = {"hip": hip}
    elif (ra and dec):
        try:
            obj = {"radec": (float(ra), float(dec))}
        except ValueError:
            return jsonify({"error": "(ra, dec) must be floats."}), 400
    
    # TODO: equinoxes & solstices: if flag, reset month & date, return flag=ve/ss/ae/ws
    
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
        'diagramId':   str(results["diagram_id"]),
        'svgData':     results["svg_data"],
        'annotations': results["annotations"]
    }), 200


@app.route("/")
@limiter.limit("5/second", override_defaults=False)
def home():
    return render_template("index.html")
