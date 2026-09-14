from rtpp_app.extensions import db
from datetime import datetime

class MeasuringUnit(db.Model):
    __tablename__ = 'measuringUnits'
    
    id = db.Column(db.String(20), primary_key=True)
    measuring_unit = db.Column(db.String(15), nullable = False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable = False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable = False)