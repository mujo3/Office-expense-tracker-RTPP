from rtpp_app.extensions import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    enabled = db.Column(db.Boolean, nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow,
                          onupdate=datetime.utcnow, nullable=False)

    # Relationship to Product (one-to-many)
    products = db.relationship('Product', back_populates='category')

    # Relationship to Invoice (one-to-many),
    # with cascade delete so that when a Category is removed, its invoices go too
    invoices = db.relationship(
        'Invoice',
        backref='category',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
