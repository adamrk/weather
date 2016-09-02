#! venv/bin/python

from flask import Flask, jsonify, make_response, render_template, request
from extract import get_data, get_temp_rain, agg_data, locations
from color import temp_to_color, rain_to_color

import time
import sys
from datetime import date, datetime, timedelta
from urllib import urlencode
from threading import Thread

"""
TODO:
	improve hourly updates (locks).
	add logging.
	allow user to set days they want.
"""

def update_data():
	for loc in locations:
		data[loc] = get_data(location = loc, offline = offline)
		temp_rain[loc] = get_temp_rain(data[loc])

	for loc in locations:
		result[loc] = []
		for x in dates:
			result[loc].append({'date':x, 'day':x.strftime('%A'), 'rain':agg_data(temp_rain[loc], x, 'rain'), 'temp':agg_data(temp_rain[loc], x, 'temp')})

	# adding colors
	for loc in locations:
		for x in result[loc]:
			x['temp']['color'] = temp_to_color(x['temp']['mean'])
			x['rain']['color'] = rain_to_color(x['rain']['mean'])

app = Flask(__name__)

@app.route('/')
def index():
	loc = request.args.get('crag', 'Gunks')
	return jsonify({'crag': loc, 'results': result[loc]})

@app.route('/page')
def page():
	loc = request.args.get('crag', 'Gunks')
	return render_template('main.html', title=loc, result=result[loc], locations=locurls, update=last_update)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': '404 Not found'}), 404)

if __name__ == '__main__':
	locurls = map(lambda x: (x, "/page?" + urlencode({'crag': x})), locations)

	offline = len(sys.argv) == 2 and sys.argv[1] == 'offline'

	# if offline fix date to sample data date
	if offline:
		today = date(2016, 8, 26)
	else:
		today = date.today()
	one_day = timedelta(days=1)
	dates = filter(lambda x: x.strftime('%A') in ['Saturday', 'Sunday'], map(lambda x: today + x*one_day, range(7)))

	# getting data:
	data = {}
	temp_rain = {}
	result = {}
	last_update = datetime.now()

	update_data()

	def threadfunc():
		while True:
			print 'thread running'
			time.sleep(3600)
			print "updating data"
			update_data()
			print "data updated"

	datathread = Thread(target=threadfunc)
	datathread.start()

	app.run(debug=True)