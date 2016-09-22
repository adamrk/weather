#! venv/bin/python

from flask import (Flask, 
				   jsonify, 
				   make_response, 
				   render_template, 
				   request, 
				   redirect)
from flask_sqlalchemy import SQLAlchemy
from extract import get_data, get_temp_rain, agg_data
from color import temp_to_color, rain_to_color
from db import Session, Crag, Forecast

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
	shift updating to use db.
"""

app = Flask(__name__)

session = Session()
locations = session.query(Crag)

def update_data():
	for loc in locations:
		data[loc.name] = get_data(location = {'lat': loc.lat / 100,
											  'lng': loc.lng / 100,
											  'wu_name': loc.wu_name},
								  offline = offline)
		temp_rain[loc.name] = get_temp_rain(data[loc.name])

	for loc in locations:
		result[loc.name] = []
		for x in dates:
			result[loc.name].append(
				{'date':x, 
				 'day':x.strftime('%A'), 
				 'rain':agg_data(temp_rain[loc.name], x, 'rain'), 
				 'temp':agg_data(temp_rain[loc.name], x, 'temp')})

	# adding colors
	for loc in locations:
		for x in result[loc.name]:
			x['temp']['color'] = temp_to_color(x['temp']['mean'])
			x['rain']['color'] = rain_to_color(x['rain']['mean'])





@app.route('/')
def index():
	loc = request.args.get('crag', 'Gunks')
	return jsonify({'crag': loc, 'results': result[loc]})

@app.route('/page')
def page():
	req_loc = request.args.get('crag')
	def_loc = request.cookies.get('default_crag')
	if req_loc != None and req_loc != def_loc:
		loc = req_loc
		setdef_link = True
	elif def_loc != None:
		loc = def_loc
		setdef_link = False
	else:
		loc = 'Gunks'
		setdef_link = True
	return render_template('main.html', title=loc,
										result=result[loc],
										locations=locurls,
										update=last_update,
										setdef_link=setdef_link
										)

@app.route('/setdefault')
def setdefault():
	loc = request.args.get('crag', 'Gunks')
	response = app.make_response(redirect('/page'))
	response.set_cookie('default_crag', value=loc)
	return response

@app.route('/setdefault')
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': '404 Not found'}), 404)

if __name__ == '__main__':
	#locurls = map(lambda x: (x, urlencode({'crag': x})), locations)
	locurls = [(x.name, urlencode({'crag': x.name})) for x in locations]
	
	offline = 'offline' in sys.argv
	noloop = ('noloop' in sys.argv) or offline


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
	if not noloop:
		datathread.start()

	app.run(debug=True)