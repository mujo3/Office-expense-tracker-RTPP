from rtpp_app.extensions import db
from datetime import datetime

class CategoryBudget(db.Model):
    __tablename__ = 'category_budgets'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    total_value = db.Column(db.Float, nullable=False, default=0.0)
    spent_value = db.Column(db.Float, nullable=False, default=0.0)
    year        = db.Column(db.Integer, nullable=False, default=datetime.utcnow().year)
    month       = db.Column(db.Integer, nullable=False, default=datetime.utcnow().month)
    recurring   = db.Column(db.Boolean, nullable=False, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship('Category', backref='category_budgets')
