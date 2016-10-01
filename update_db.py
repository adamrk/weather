#! venv/bin/python

from extract import (get_data, 
    get_temp_rain, 
    agg_data,
    get_actual_json,
    get_actual_temp_rain)
from db import Session, Forecast, Crag, Actual
from sys import argv
from datetime import datetime, timedelta

offline = 'offline' in argv

def update_forecasts():
    # add current forecasts to db
    session = Session()
    crags = session.query(Crag)
    updatetime = datetime.now() #all entries to have exact same pred time
    for crag in crags:
        location = {'lat' : crag.lat / 100.0, ## stored as int in db
            'lng' : crag.lng / 100.0, ## stored as int in db
            'wu_name' : crag.wu_name }
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
                    pred_time=updatetime,
                    pred_for=day['date']
                    )
                session.add(forecast)
    session.commit()
    session.close()

def update_actual(date):
    # add actual weather for date to db
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
    if sys.argv[1] == "forecast":
        update_forecasts()
    if sys.argv[1] == "actual":
        update_actual(datetime.today() - timedelta(days=1))