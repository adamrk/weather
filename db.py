
from sqlalchemy import ( create_engine, 
                         Column, 
                         Integer, 
                         String, 
                         DateTime,
                         Date,
                         ForeignKey,)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import os

engine = create_engine('sqlite:///' + os.environ['DB_PATH'])
Base = declarative_base()

class Crag(Base):
    __tablename__ = 'crags'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ## Note lat and lng are scaled by 100 e.g. 75.65 lat stored as 7565
    lat = Column(Integer)
    lng = Column(Integer)

    forecasts = relationship("Forecast", back_populates='crag')

    def __repr__(self):
        return "<Crag(name=%s, lat=%d, lng=%d)>" % (self.name, self.lat, self.lng)

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
        return "<Forecast(service=%s, crag=%s, temp=%d, rain=%d, pred_for=%s)>" % (
            self.service, self.crag_id, self.temp, 
            self.rain, self.pred_for.ascftime("%b %d %y"))

if __name__ == "__main__":
    Base.metadata.create_all(engine)        


