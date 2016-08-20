#! venv/bin/python

from flask import Flask, jsonify, make_response
from extract import get_data, get_temp_rain, agg_data

app = Flask(__name__)

data = get_data()
temp_rain = get_temp_rain(data)
result = {}
for x in ['Saturday', 'Sunday']:
	result[x] = {'rain':agg_data(temp_rain, x, 'rain'), 'temp':agg_data(temp_rain, x, 'temp')}

@app.route('/')
def index():
	return jsonify(result)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': '404 Not found'}), 404)

if __name__ == '__main__':
	app.run(debug=True)