from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from rtpp_app.extensions import db
from rtpp_app.models.invoice import Invoice
from rtpp_app.models.category import Category
from rtpp_app.models.vendor import Vendor
from rtpp_app.models.budgets import Budget
from datetime import datetime
from functools import wraps

analytics_bp = Blueprint(
    'analytics',
    __name__,
    template_folder='../templates/analytics',
    url_prefix='/analytics'
)

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
            if current_user.role not in roles:
                return abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator

@analytics_bp.route('/', methods=['GET'])
@login_required
@roles_required('admin', 'manager')
def dashboard():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')


    invoice_query = db.session.query(Invoice)


    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            invoice_query = invoice_query.filter(Invoice.date.between(start, end))
        except ValueError:
            invoice_query = invoice_query
    invoices = invoice_query.all()

    invoice_ids = [inv.id for inv in invoices]


    category_data = db.session.query(
        Category.name,
        func.coalesce(func.sum(Invoice.total_incl_vat), 0)
        ).outerjoin(Invoice, Invoice.category_id == Category.id)\
        .filter(Invoice.id.in_(invoice_ids))\
            .group_by(Category.name).all()


    vendor_data = db.session.query(
        Vendor.vendor_name,
        func.coalesce(func.sum(Invoice.total_incl_vat), 0)
        ).join(Invoice, Invoice.vendor_id == Vendor.id)\
        .filter(Invoice.id.in_(invoice_ids))\
            .group_by(Vendor.vendor_name).all()
     


    from sqlalchemy.orm import aliased

    InvoiceAlias = aliased(Invoice)
    
    budget_data = db.session.query(
        Category.name,
        func.coalesce(func.sum(InvoiceAlias.total_incl_vat), 0).label("total_spent"),
        Budget.total_budget
        ).join(Budget, Budget.category_id == Category.id)\
        .outerjoin(InvoiceAlias, (InvoiceAlias.category_id == Category.id) & (InvoiceAlias.id.in_(invoice_ids)))\
            .group_by(Category.name, Budget.total_budget).all()

    return render_template(
        'analytics.html',
        category_data=category_data,
        vendor_data=vendor_data,
        budget_data=budget_data,
        start_date=start_date,
        end_date=end_date
    )
