#! venv/bin/python

import bs4
import re
import requests
import os
from urllib2 import urlopen
from datetime import date, datetime, timedelta
#from urlparse import urlunparse


"""
TODO:

    add some unittests

"""

def previous_day(day):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    inx = days.index(day)
    return days[(inx - 1) % 7]

############## NOAA ####################

# To extract the temp in two steps
regex_temp_sentence = re.compile('(H|h)igh near -?\d{1,3}')
regex_temp_digits = re.compile('-?\d{1,3}')

def get_temp(string):
    temp_sen_match = re.search(regex_temp_sentence, string)
    if temp_sen_match == None:
        result = None
    else:
        result = re.search(regex_temp_digits, temp_sen_match.group()).group()
    return result

# To extract chance of rain in two steps
regex_rain_sentence = re.compile('Chance of precipitation is \d{2}%')
regex_rain_digits = re.compile('\d{2}')

def get_rain(string):
    rain_sen_match = re.search(regex_rain_sentence, string)
    if rain_sen_match == None:
        result = 0
    else:
        result = re.search(regex_rain_digits, rain_sen_match.group()).group()
    return result


def get_noaa_soup():
    html = urlopen("http://forecast.weather.gov/MapClick.php?lat=41.747589209000466&lon=-74.08680975599964")
    return bs4.BeautifulSoup(html, 'html.parser')


def get_noaa_temp_rain(soup):
    """ Return an array of dicts with attributes 'day', 'temp', 'rain' """

    body = soup.find(id='detailed-forecast-body')
    daily_forecasts = map(lambda x: {'day' : unicode(x.div.b.string), 'forecast' : unicode(x.find_all('div')[1].string)}, body.contents[1:-1])
    daily_forecasts = filter(lambda x: x['day'].find('Night') < 0 and x['day'].find('Tonight') < 0, daily_forecasts)
    daily_high_rain = map(lambda x: {'day': x['day'], 'temp': int(get_temp(x['forecast'])), 'rain': int(get_rain(x['forecast']))}, daily_forecasts)
    # sometimes current day is listed as today or this afternoon. change based on later dates.
    last_day = daily_high_rain[1]['day']
    daily_high_rain[0]['day'] = previous_day(last_day)
    # find if first day is today or tomorrow. Then assign a date to each element
    curr_date = date.today()
    one_day = timedelta(days=1)
    if daily_high_rain[0]['day'] == curr_date.strftime('%A'):
        first_date = curr_date
    else:
        first_date = curr_date + one_day

    for i in range(len(daily_high_rain)):
        daily_high_rain[i]['date'] = first_date + (one_day*i)

    return daily_high_rain[:9]

################## WUnderground ##################
try:
    api_key = os.environ['API_KEY']
except KeyError:
    print "please set the API_KEY to for wunderground."
    exit()

def get_wu_json():
    response = requests.get('http://api.wunderground.com/api/%s/forecast10day/q/NY/New_Paltz.json' % api_key)
    return response.json()

def get_wu_temp_rain(json):
    daily_forecasts = json['forecast']['simpleforecast']['forecastday']
    daily_high_rain = map(lambda x: {
        'day': x['date']['weekday'], 
        'temp': int(x['high']['fahrenheit']), 
        'rain': int(x['pop']),
        'date': date(x['date']['year'], x['date']['month'], x['date']['day'])}, daily_forecasts)
    return daily_high_rain[:9]
"""
################## Open Weather Map ##########################
try:
    open_api_key = os.environ['OPEN_API_KEY']
except KeyError:
    print "please set the OPEN_API_KEY for Open Weather Map"
    exit()

def get_owm_json():
    response = requests.get('http://api.openweathermap.org/data/2.5/forecast/daily?lat=41.747589&lon=-74.086807&cnt=7&mode=json&units=imperial&appid=%s' % open_api_key)
    return response.json()

def get_owm_temp_rain(json):
    daily_forecasts = json['list']
    daily_high_rain = map(lambda x: {'day': date.fromtimestamp(x['dt']).strftime("%A"), 'temp': x['temp']['max'], 'rain': x.get('rain') if x.get('rain') else 0}, daily_forecasts)
    return daily_high_rain
"""
###################### Forecast.ai ###########################
try:
    fore_api_key = os.environ['FORE_API_KEY']
except KeyError:
    print "please set the FORE_API_KEY for forecast.ai"
    exit()

def get_fore_json():
    response = requests.get('https://api.forecast.io/forecast/%s/41.747589,-74.086807' % fore_api_key )
    return response.json()

def get_fore_temp_rain(json):
    daily_forecasts = json['daily']['data']
    daily_high_rain = map(lambda x: {
        'day': date.fromtimestamp(x['time']).strftime('%A'), 
        'temp': int(x['temperatureMax']), 
        'rain': int(float(x['precipProbability'])*100),
        'date': date.fromtimestamp(x['time']) }, daily_forecasts)
    return daily_high_rain[:9]


######################## Collecting and Aggregating ###########################
def get_data():
    soup = get_noaa_soup()
    json1 = get_wu_json()
    json2 = get_fore_json()
    return {'noaa': soup, 'wu': json1, 'fore': json2}

def get_temp_rain(data):
    noaa_tr = get_noaa_temp_rain(data['noaa'])
    wu_tr = get_wu_temp_rain(data['wu'])
    fore_tr = get_fore_temp_rain(data['fore'])
    return {'noaa': noaa_tr, 'wu': wu_tr, 'fore': fore_tr}

def agg_data(data, date, temp_or_rain):
    values = []
    num_values = 0
    for x in data.values():
        for y in x:
            if y['day'] == day:
                values.append(y[temp_or_rain])
                num_values += 1
    mean = float(sum(values)) / num_values
    dev = pow(sum(map(lambda x: pow(x - mean, 2), values)) / (num_values - 1), 0.5)
    return {'mean': mean, 'dev': dev}

def print_data():
    soup = get_noaa_soup()
    noaa_data = get_noaa_temp_rain(soup)
    print 'data from NOAA:'
    for x in noaa_data:
        print 'on %s (%s) the temp is %d and rain is %d' % (x['day'], x['date'].strftime('%a, %b, %d'), x['temp'], x['rain'])

    json = get_wu_json()
    wu_data = get_wu_temp_rain(json)
    print 'data from WUnderground:'
    for x in wu_data:
        print 'on %s (%s) the temp is %d and rain is %d' % (x['day'], x['date'].strftime('%a, %b, %d'), x['temp'], x['rain'])

    json2 = get_fore_json()
    fore_data = get_fore_temp_rain(json2)
    print 'data from Forecast.ai:'
    for x in fore_data:
        print 'on %s (%s) the temp is %d and rain is %d' % (x['day'], x['date'].strftime('%a, %b, %d'), x['temp'], x['rain'])

if  __name__ == "__main__":
    print_data()    