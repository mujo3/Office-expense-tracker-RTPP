from datetime import datetime
from rtpp_app.extensions import db

class Invoice(db.Model):
    __tablename__ = "invoice"


    id = db.Column(db.Integer, primary_key=True)

    # step 1
    invoice_number = db.Column(db.String(100), nullable=False)
    fiscal_number  = db.Column(db.String(32))   # optional
    order_number   = db.Column(db.String(64))   # optional

    # step 2
    date_issue     = db.Column(db.Date, nullable=False)
    date_delivery  = db.Column(db.Date)
    due_date       = db.Column(db.Date)
    place_issue    = db.Column(db.String(64))
    payment_method = db.Column(db.String(32))   # e.g. Cash, Virman
    reference      = db.Column(db.String(256))  # free text

    # step 3
    total_excl_vat = db.Column(db.Float, nullable=False)
    vat_amount     = db.Column(db.Float, nullable=False)
    total_incl_vat = db.Column(db.Float, nullable=False)

    # FK
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("category.id", ondelete='CASCADE'),
        nullable=False
    )
    vendor_id   = db.Column(
        db.Integer,
        db.ForeignKey("vendor.id"),
        nullable=False
    )

    # Relationships
    vendor        = db.relationship("Vendor", back_populates="invoices")
    invoice_items = db.relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
