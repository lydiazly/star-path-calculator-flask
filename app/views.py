# app/views.py
from flask import request, jsonify, render_template, current_app as app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from core import get_coords

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


@app.route("/coords", methods=["GET"])
@limiter.limit("4/second", override_defaults=False)
def coords():
    year   = request.args.get("year")
    month  = request.args.get("month")
    day    = request.args.get("day")
    hour   = request.args.get("hour")
    minute = request.args.get("minute")
    second = request.args.get("second")

    if not year and year != 0:
        return jsonify({"error": "Year is required."}), 400

    try:
        year   = int(year)
        month  = int(month)
        day    = int(day)
        hour   = int(hour)
        minute = int(minute)
        second = int(second)
    except ValueError:
        return jsonify({"error": "Date and time must be integers."}), 400

    try:
        results = get_coords(year, month, day, hour, minute, second)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "year":    str(year),
        "month":   str(month),
        "day":     str(day),
        "hour":    str(hour),
        "minute":  str(minute),
        "second":  str(second),
        "results": results,
    }), 200


@app.route("/")
@limiter.limit("5/second", override_defaults=False)
def home():
    return render_template("index.html")
