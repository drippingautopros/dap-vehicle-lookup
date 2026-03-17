import json
import os
from flask import Flask, request, jsonify
from collections import Counter

app = Flask(__name__)

# Load vehicle data
with open('vehicle_data.json', 'r') as f:
    raw_data = json.load(f)

# Build lookup tables
exact_lookup = {}
fallback_lookup = {}

for row in raw_data:
    if len(row) == 5:
        make, model, year, submodel, size = row
        exact_lookup[(make.lower().strip(), model.lower().strip(), year.lower().strip(), submodel.lower().strip())] = size
        key3 = (make.lower().strip(), model.lower().strip(), year.lower().strip())
        if key3 not in fallback_lookup:
            fallback_lookup[key3] = []
        fallback_lookup[key3].append(size)

fallback_final = {k: Counter(v).most_common(1)[0][0] for k, v in fallback_lookup.items()}

@app.route('/')
def home():
    return jsonify({
        "service": "Dripping Auto Pros Vehicle Size Lookup",
        "status": "running",
        "total_vehicles": len(exact_lookup),
        "usage": "/lookup?make=Ford&model=F-150&year=2015&submodel=XLT"
    })

@app.route('/lookup')
def lookup():
    make = request.args.get('make', '').lower().strip()
    model = request.args.get('model', '').lower().strip()
    year = request.args.get('year', '').lower().strip()
    submodel = request.args.get('submodel', '').lower().strip()

    if not make or not model or not year:
        return jsonify({
            "error": "Missing required parameters. Please provide make, model, and year.",
            "example": "/lookup?make=Ford&model=F-150&year=2015&submodel=XLT"
        }), 400

    # Try exact match first
    exact_key = (make, model, year, submodel)
    if exact_key in exact_lookup:
        return jsonify({
            "make": make.title(),
            "model": model.title(),
            "year": year,
            "submodel": submodel.title(),
            "size": exact_lookup[exact_key],
            "match_type": "exact"
        })

    # Try fallback (make/model/year only)
    fallback_key = (make, model, year)
    if fallback_key in fallback_final:
        return jsonify({
            "make": make.title(),
            "model": model.title(),
            "year": year,
            "submodel": submodel.title(),
            "size": fallback_final[fallback_key],
            "match_type": "approximate"
        })

    return jsonify({
        "make": make.title(),
        "model": model.title(),
        "year": year,
        "submodel": submodel.title(),
        "size": "Unknown",
        "match_type": "not_found"
    }), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
