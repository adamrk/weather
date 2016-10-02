#! venv/bin/python

from setup import db

class Crag(db.Model):
    #__tablename__ = 'crags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ## Note lat and lng are scaled by 100 e.g. 75.65 lat stored as 7565
    lat = db.Column(db.Integer)
    lng = db.Column(db.Integer)
    wu_name = db.Column(db.String)

    #forecasts = db.relationship("Forecast", backref=db.backref('crag'))
    #actuals = db.relationship("Actual", backref=db.backref('crag'))

    def __repr__(self):
        return "<Crag(name=%s, lat=%d, lng=%d, wu_name=%s)>" % (
            self.name, self.lat, self.lng, self.wu_name)

class Forecast(db.Model):
    #__tablename__ = 'forecasts'

    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String, nullable=False)
    crag_id = db.Column(db.Integer, db.ForeignKey('crag.id'))
    temp = db.Column(db.Integer)
    rain = db.Column(db.Integer)
    pred_time = db.Column(db.DateTime)
    pred_for = db.Column(db.Date)

    crag = db.relationship("Crag", backref=db.backref("forecasts", lazy='dynamic'))

    def __repr__(self):
        return "<Forecast(service=%s, crag=%s, temp=%d, rain=%d, pred_time=%s, pred_for=%s)>" % (
            self.service, self.crag_id, self.temp, 
            self.rain, self.pred_time.strftime("%b %d %y, %H:%M"), 
            self.pred_for.strftime("%b %d %y"))

class Actual(db.Model):
    #__tablename__ = 'actuals'

    id = db.Column(db.Integer, primary_key=True)
    temp = db.Column(db.Integer)
    rain = db.Column(db.Integer)
    date = db.Column(db.Date)
    crag_id = db.Column(db.Integer, db.ForeignKey('crag.id'))

    crag = db.relationship("Crag", backref=db.backref("actuals", lazy='dynamic'))

    def __repr__(self):
        return "<Actual(crag=%s, temp=%d, rain=%s, date=%s>" % (
            self.crag_id, self.temp, self.rain, 
            self.date.strftime("%b %d %y"))

if __name__ == "__main__":
    ## to setup db create all tables and load in the static crag data
    log.info("creating tables")
    db.create_all()
    crags = [
        Crag(name="Gunks", 
             lat=4174, 
             lng=-7408, 
             wu_name="NY/New_Paltz"),
        Crag(name="Red River Gorge", 
             lat=3779, 
             lng=-8370, 
             wu_name="KY/Slade"),
        Crag(name="Joshua Tree", 
             lat=3401, 
             lng=-11616, 
             wu_name="CA/Joshua_Tree")
        ]
    for crag in crags:
        db.session.add(crag)
    db.session.commit()
    log.info("done creating tables")