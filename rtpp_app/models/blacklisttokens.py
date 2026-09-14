from rtpp_app.extensions import db
from datetime import datetime

class BlacklistToken(db.Model):
    __tablename__ = 'blackListTokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), unique = True, nullable = False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable = False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable = False)