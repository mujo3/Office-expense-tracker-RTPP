from rtpp_app.extensions import db
from datetime import datetime

class Budget(db.Model):
    __tablename__ = 'budget'
    
    id = db.Column(db.Integer, primary_key=True)
    total_budget = db.Column(db.Float, nullable = False)
    spent_budget = db.Column(db.Float, nullable = False)
    year = db.Column(db.Integer, nullable = False)
    month = db.Column(db.Integer, nullable = False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable = False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable = False)
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  # ✅ OVO MORA POSTOJATI

    category = db.relationship('Category', backref='budgets')