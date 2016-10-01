#! venv/bin/python

from flask import (Flask, 
				   jsonify, 
				   make_response, 
				   render_template, 
				   request, 
				   redirect)
from extract import get_data, get_temp_rain, agg_data
from color import temp_to_color, rain_to_color
from db import Session, Crag, Forecast
from sqlalchemy import func

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

app = Flask(__name__)

session = Session()
locations = session.query(Crag)

def update_data2():
	services = ["wu", "noaa", "fore"]
	# filter query to most recent results
	tr_query = session.query(Forecast)
	maxtime = session.query(func.max(Forecast.pred_time))
	maxtime = max([x.pred_time for x in tr_query])
	#maxtime = max([x.pred_time for x in tr_query.filter(
	#	Forecast.pred_time > datetime.now() - timedelta(days=1))])
	results = tr_query.filter(Forecast.pred_time == maxtime)

	# add each result to the temp_rain structure
	tr = {}
	for loc in locations:
		tr[loc.name] = {}
		for ser in services:
			tr[loc.name][ser] = []
	
	for res in results:
		crag_name = [x.name for x in 
			locations.filter(Crag.id == res.crag_id)][0]
		
		tr[crag_name][res.service].append({
			'day': res.pred_for.strftime('%A'),
			'temp': res.temp,
			'rain': res.rain,
			'date': res.pred_for})

	return tr, maxtime

def aggregate(tr):
	result = {}
	for loc in locations:
		result[loc.name] = []
		for x in dates:
			result[loc.name].append(
				{'date':x, 
				 'day':x.strftime('%A'), 
				 'rain':agg_data(tr[loc.name], x, 'rain'), 
				 'temp':agg_data(tr[loc.name], x, 'temp')})

	for loc in locations:
		for x in result[loc.name]:
			x['temp']['color'] = temp_to_color(x['temp']['mean'])
			x['rain']['color'] = rain_to_color(x['rain']['mean'])

	return result

##################### Defining Views ##########################
@app.route('/')
def index():
	loc = request.args.get('crag', 'Gunks')
	return jsonify({'crag': loc, 'results': aggregated[loc]})

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
										result=aggregated[loc],
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

###################### Exec #############################

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
	alldates = [today + x * one_day for x in range(7)]
	dates = [x for x in alldates if x.strftime('%A') in 
		['Saturday', 'Sunday']] 
	
	temp_rain, last_update = update_data2()
	aggregated = aggregate(temp_rain)

	def threadfunc():
		while True:
			print 'thread running'
			time.sleep(3600)
			print "updating data"
			temp_rain, last_update = update_data2()
			aggregated = aggregate(temp_rain)			
			print "data updated"

	datathread = Thread(target=threadfunc)
	if not noloop:
		datathread.start()

	app.run(debug=True)