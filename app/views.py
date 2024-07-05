# app/views.py
from flask import request, jsonify, render_template
from app import app
from core import get_coords

@app.route('/coords', methods=['GET'])
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
        return jsonify({'error': e}), 500

    return jsonify({'year': year, 'results': results}), 200

@app.route('/')
def home():
    return render_template('index.html')