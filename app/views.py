# app/views.py
from flask import request, jsonify, render_template
from app import app
from app.utils import get_equinoxes, get_solstices
from skyfield.api import load

@app.route('/get_coords', methods=['GET'])
def get_coords():
    year = request.args.get('year')
    
    if year is None:
        return jsonify({'error': 'Year is required'}), 400

    try:
        year = int(year)
    except ValueError:
        return jsonify({'error': 'Year must be an integer'}), 400

    ts = load.timescale()
    t = ts.ut1(year, 1, 1, 12, 0, 0)

    try:
        vernal_ra_j2000, vernal_dec_j2000, autumnal_ra_j2000, autumnal_dec_j2000 = get_equinoxes(t)
        summer_ra_j2000, summer_dec_j2000, winter_ra_j2000, winter_dec_j2000 = get_solstices(t)
    except Exception as e:
        return jsonify({'error': f'Error in calculation: {e}'}), 500

    results = {
        'vernal_ra': str(vernal_ra_j2000), 'vernal_dec': str(vernal_dec_j2000),
        'autumnal_ra': str(autumnal_ra_j2000), 'autumnal_dec': str(autumnal_dec_j2000),
        'summer_ra': str(summer_ra_j2000), 'summer_dec': str(summer_dec_j2000),
        'winter_ra': str(winter_ra_j2000), 'winter_dec': str(winter_dec_j2000),
    }

    return jsonify({'year': year, 'results': results})

@app.route('/')
def home():
    return render_template('index.html')