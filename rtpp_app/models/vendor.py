from rtpp_app.extensions import db
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = 'vendor'

    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(100), nullable=False)  # matches DB column
    vat_number = db.Column(db.String(20), nullable=False, unique=True)
    account_number = db.Column(db.String(50), nullable=False)
    bank = db.Column(db.String(100), nullable=False)
    adress = db.Column(db.String(200), nullable=False)
    vendorCity = db.Column(db.String(50), nullable=False)
    vendorTelephone = db.Column(db.String(20), nullable=False)
    vendorEmail = db.Column(db.String(100), nullable=False)
    vendorTransact = db.Column(db.String(100), nullable=False)
    supportsAvans = db.Column(db.Boolean, nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


    invoices = db.relationship("Invoice", back_populates="vendor", cascade="all, delete-orphan")
