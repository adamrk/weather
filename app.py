#! venv/bin/python

from flask import Flask, jsonify, make_response, render_template
from extract import get_data, get_temp_rain, agg_data, locations
from color import temp_to_color, rain_to_color
import time
import sys
from datetime import date, timedelta

"""
TODO:
	change date display to be small.
	choose location based on get request.
	update data every hour.
"""

app = Flask(__name__)

offline = len(sys.argv) == 2 and sys.argv[1] == 'offline'
data = {}
temp_rain = {}
for loc in locations:
	data[loc] = get_data(location = loc, offline = offline)
	temp_rain[loc] = get_temp_rain(data[loc])

# if offline fix date to sample data date
if offline:
	today = date(2016, 8, 26)
else:
	today = date.today()
one_day = timedelta(days=1)
dates = filter(lambda x: x.strftime('%A') in ['Saturday', 'Sunday'], map(lambda x: today + x*one_day, range(7)))

result = {}
for loc in locations:
	result[loc] = []
	for x in dates:
		result[loc].append({'date':x, 'day':x.strftime('%A'), 'rain':agg_data(temp_rain[loc], x, 'rain'), 'temp':agg_data(temp_rain[loc], x, 'temp')})

# adding colors
for loc in locations:
	for x in result[loc]:
		x['temp']['color'] = temp_to_color(x['temp']['mean'])
		x['rain']['color'] = rain_to_color(x['rain']['mean'])

@app.route('/')
def index():
	return jsonify(result['Gunks'])

@app.route('/page')
def page():
	return render_template('main.html', result=result['Gunks'])

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': '404 Not found'}), 404)



if __name__ == '__main__':
	app.run(debug=True)
	while(True):
		data = get_data()
		temp_rain = get_temp_rain(data)
		result = []
		for x in ['Saturday', 'Sunday']:
			result.append({'day':x, 'rain':agg_data(temp_rain, x, 'rain'), 'temp':agg_data(temp_rain, x, 'temp')})

		# adding colors
		for x in result:
			x['temp']['color'] = temp_to_color(x['temp']['mean'])
			x['rain']['color'] = rain_to_color(x['rain']['mean'])
		time.sleep(3600)
