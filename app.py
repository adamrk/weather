#! venv/bin/python

from flask import Flask, jsonify, make_response, render_template
from extract import get_data, get_temp_rain, agg_data
from color import temp_to_color, rain_to_color

app = Flask(__name__)

data = get_data()
temp_rain = get_temp_rain(data)
result = []
for x in ['Saturday', 'Sunday']:
	result.append({'day':x, 'rain':agg_data(temp_rain, x, 'rain'), 'temp':agg_data(temp_rain, x, 'temp')})

# adding colors
for x in result:
	x['temp']['color'] = temp_to_color(x['temp']['mean'])
	x['rain']['color'] = rain_to_color(x['rain']['mean'])

@app.route('/')
def index():
	return jsonify(result)

@app.route('/page')
def page():
	return render_template('main.html', result=result)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': '404 Not found'}), 404)



if __name__ == '__main__':
	app.run(debug=True)