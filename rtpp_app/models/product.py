from rtpp_app.extensions import db
from rtpp_app.models.invoiceitem import InvoiceItem
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)

    item_name = db.Column(db.String(100), nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable = False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable = False)

    #Foreign key to Measuring Units
    measuring_units_id = db.Column(db.String(20), db.ForeignKey('measuringUnits.id'), nullable = False)
    
    # Foreign key to Category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    # Relationships
    category = db.relationship('Category', back_populates='products')

    invoice_items = db.relationship(
        'InvoiceItem',
        back_populates='product'
    )
