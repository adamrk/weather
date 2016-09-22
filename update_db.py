from extract import (get_data, 
    get_temp_rain, 
    agg_data,
    get_actual_json,
    get_actual_temp_rain)
from db import Session, Forecast, Crag, Actual
from sys import argv
from datetime import datetime

offline = 'offline' in argv

session = Session()
crags = session.query(Crag)
data = {}
temp_rain = {}
session.close()

def update_data():
    session = Session()
    for crag in crags:
        location = {'lat' : crag.lat / 100.0, 'lng' : crag.lng / 100.0, 'wu_name' : crag.wu_name }
        data = get_data(location = {
            'lat' : crag.lat / 100.0,
            'lng' : crag.lng / 100.0,
            'wu_name' : crag.wu_name }
            , offline = offline)
        temp_rain = get_temp_rain(data)
        for x in temp_rain:
            for day in temp_rain[x]:
                forecast = Forecast(
                    service=x,
                    crag_id=crag.id,
                    temp=day['temp'],
                    rain=day['rain'],
                    pred_time=datetime.now(),
                    pred_for=day['date']
                    )
                session.add(forecast)
    session.commit()
    session.close()

def update_actual(date):
    session = Session()
    for crag in crags:
        location = {'lat' : crag.lat / 100.0, 'lng' : crag.lng / 100.0}
        json = get_actual_json(location, date)
        temp_rain = get_actual_temp_rain(json)
        actual = Actual(
            crag_id=crag.id,
            temp=temp_rain['temp'],
            rain=temp_rain['rain'],
            date=date
            )
        print actual
        session.add(actual)
    session.commit()
    session.close()

if __name__ == "__main__":
    update_data()

"""
        forecast = Forecast()
    for loc in locations:
        result[loc] = []
        for x in dates:
            result[loc].append(
                {'date':x, 
                 'day':x.strftime('%A'), 
                 'rain':agg_data(temp_rain[loc], x, 'rain'), 
                 'temp':agg_data(temp_rain[loc], x, 'temp')})

    # adding colors
    for loc in locations:
        for x in result[loc]:
            x['temp']['color'] = temp_to_color(x['temp']['mean'])
            x['rain']['color'] = rain_to_color(x['rain']['mean'])
"""