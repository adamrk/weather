from extract import get_data, get_temp_rain, agg_data
from db import session, Forecast, Crag
from sys import argv
from datetime import datetime
#import pdb

offline = 'offline' in argv

crags = session.query(Crag)
data = {}
temp_rain = {}


##### Working here database doesn't seem to be updating
def update_data():
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
                print "adding: "
                print forecast
                session.add(forecast)
#    pdb.set_trace()
    print "committing: "
    print session.is_active
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