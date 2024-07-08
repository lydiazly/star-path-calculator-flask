# app/views.py
from flask import request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app import app
from core import get_coords

# Initialize the limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["720 per hour", "60 per minute"],
    storage_uri='memory://',
    strategy='fixed-window'
)

@app.errorhandler(429)
def ratelimit_error(e):
    print(str(e))
    return jsonify({'error': f"Too Many Requests: {str(e.description)}. Please try again later."}), 429

@app.route('/coords', methods=['GET'])
@limiter.limit("5/second", override_defaults=False)
def coords():
    year = request.args.get('year')
    
    if year is None:
        return jsonify({'error': 'Year is required.'}), 400

    try:
        year = int(year)
    except ValueError:
        return jsonify({'error': 'Year must be an integer.'}), 400

    try:
        results = get_coords(year)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'year': year, 'results': results}), 200

@app.route('/')
def home():
    return render_template('index.html')