#! venv/bin/python

from flask import (Flask, 
				   jsonify, 
				   make_response, 
				   render_template, 
				   request, 
				   redirect)
#from flask_sqlalchemy import SQLAlchemy
from extract import get_data, get_temp_rain, agg_data
from color import temp_to_color, rain_to_color
from db import Crag, Forecast
#from sqlalchemy import func
from setup import app, db
import time
import sys
from datetime import date, datetime, timedelta
from urllib import urlencode
from threading import Thread
import os

"""
TODO:
	improve hourly updates (locks).
	allow user to set days they want.
	change display timezone
"""

locations = Crag.query.all()
locurls = [(x.name, urlencode({'crag': x.name})) for x in locations]
	
#offline = 'offline' in sys.argv

def update_data(crag_name):
	services = ["wu", "noaa", "fore"]
	# filter query to most recent results
	maxtime = db.session.query(db.func.max(Forecast.pred_time)).scalar()
	print "got maxtime"
	location = [x for x in locations if x.name == crag_name][0]
	results = (db.session.query(Forecast)
		.filter(Forecast.crag_id == location.id)
		.all())


	# add each result to the temp_rain structure
	tr = {}
	for ser in services:
		tr[ser] = []
	
	for res in results:
		tr[res.service].append({
			'day': res.pred_for.strftime('%A'),
			'temp': res.temp,
			'rain': res.rain,
			'date': res.pred_for})

	return tr, maxtime

def aggregate(tr, dates):
	result = []
	for x in dates:
		result.append(
			{'date':x, 
			 'day':x.strftime('%A'), 
			 'rain':agg_data(tr, x, 'rain'), 
			 'temp':agg_data(tr, x, 'temp')})

	for x in result:
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
	# if offline fix date to sample data date
#	if offline:
#		today = date(2016, 8, 26)
#	else:
	today = date.today()
	# set dates to dates of interest
	one_day = timedelta(days=1)
	alldates = [today + x * one_day for x in range(7)]
	dates = [x for x in alldates if x.strftime('%A') in 
		['Saturday', 'Sunday']] 
	
	# determine which location user wants
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

	temp_rain, last_update = update_data(loc)
	aggregated = aggregate(temp_rain, dates)

	return render_template('main.html', title=loc,
										result=aggregated,
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
	
	app.run(debug=True)