from rtpp_app.extensions import db
from datetime import datetime

class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id', ondelete = 'CASCADE'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price_excl_vat = db.Column(db.Float, nullable=False)
    unit_price_incl_vat = db.Column(db.Float, nullable=False)
    total_excl_vat = db.Column(db.Float, nullable=False)
    total_incl_vat = db.Column(db.Float, nullable = False)
    discount = db.Column(db.Float, nullable = False)
    vat_rate = db.Column(db.Float, nullable=False)
    vat_amount = db.Column(db.Float, nullable=False)
    product_code = db.Column(db.String)

    item_name         = db.Column(db.String(200), nullable=False)
    measuring_unit    = db.Column(db.String(50), nullable=False)

    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable = False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable = False)


    invoice = db.relationship('Invoice', back_populates='invoice_items', passive_deletes=True)
    product = db.relationship('Product', back_populates='invoice_items')
    
