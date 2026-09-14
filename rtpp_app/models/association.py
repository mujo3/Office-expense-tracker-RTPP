from rtpp_app.extensions import db

invoice_product = db.Table(
    'invoice_product',
    db.Column('invoice_id', db.Integer, db.ForeignKey('invoice.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)
