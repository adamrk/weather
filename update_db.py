#! venv/bin/python

from extract import (get_data, 
    get_temp_rain, 
    agg_data,
    get_actual_json,
    get_actual_temp_rain)
from db import Forecast, Crag, Actual
from setup import db
from sys import argv
from datetime import datetime, timedelta
import logging


log = logging.basicConfig(
    filename = "app.log",
    format = "%(levelname)-10s %(asctime)s %(message)s",
    level = logging.INFO
)

log = logging.getLogger('app')

offline = 'offline' in argv



def update_forecasts():
    log.info("start updating forecasts")
    # add current forecasts to db
    crags = Crag.query.all()
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
                db.session.add(forecast)
    db.session.commit()
    log.info("finish updating forecasts")

def update_actual(date):
    log.info("start updating actuals")
    # add actual weather for date to db
    crags = Crag.query.all()
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
        db.session.add(actual)
    db.session.commit()
    log.info("finish updating actual")

if __name__ == "__main__":
    if argv[1] == "forecast":
        update_forecasts()
    if argv[1] == "actual":
        update_actual(datetime.today() - timedelta(days=1))