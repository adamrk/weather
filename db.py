#! venv/bin/python

from sqlalchemy import ( create_engine, 
                         Column, 
                         Integer, 
                         String, 
                         DateTime,
                         Date,
                         ForeignKey,
                         )
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()
engine = create_engine('sqlite:///' + os.environ['DB_PATH'])
Session = sessionmaker(bind=engine)
session = Session()

class Crag(Base):
    __tablename__ = 'crags'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ## Note lat and lng are scaled by 100 e.g. 75.65 lat stored as 7565
    lat = Column(Integer)
    lng = Column(Integer)
    wu_name = Column(String)

    forecasts = relationship("Forecast", back_populates='crag')
    actuals = relationship("Actual", back_populates='crag')

    def __repr__(self):
        return "<Crag(name=%s, lat=%d, lng=%d, wu_name=%s)>" % (
            self.name, self.lat, self.lng, self.wu_name)

class Forecast(Base):
    __tablename__ = 'forecasts'

    id = Column(Integer, primary_key=True)
    service = Column(String, nullable=False)
    crag_id = Column(Integer, ForeignKey('crags.id'))
    temp = Column(Integer)
    rain = Column(Integer)
    pred_time = Column(DateTime)
    pred_for = Column(Date)

    crag = relationship("Crag", back_populates="forecasts")

    def __repr__(self):
        return "<Forecast(service=%s, crag=%s, temp=%d, rain=%d, pred_time=%s, pred_for=%s)>" % (
            self.service, self.crag_id, self.temp, 
            self.rain, self.pred_time.strftime("%b %d %y, %H:%M"), 
            self.pred_for.strftime("%b %d %y"))

class Actual(Base):
    __tablename__ = 'actuals'

    id = Column(Integer, primary_key=True)
    temp = Column(Integer)
    rain = Column(Integer)
    date = Column(Date)
    crag_id = Column(Integer, ForeignKey('crags.id'))

    crag = relationship("Crag", back_populates="actuals")

    def __repr__(self):
        return "<Actual(crag=%s, temp=%d, rain=%s, date=%s>" % (
            self.crag_id, self.temp, self.rain, 
            self.date.strftime("%b %d %y"))

if __name__ == "__main__":
    ## to setup db create all tables and load in the static crag data
    Base.metadata.create_all(engine)
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
        session.add(crag)
    session.commit()
    session.close()





