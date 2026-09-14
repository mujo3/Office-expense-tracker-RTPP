from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user, logout_user
from rtpp_app.extensions import db
from rtpp_app.forms import InvoiceForm
from rtpp_app.models.vendor import Vendor
from rtpp_app.models.user import User
from rtpp_app.models.category import Category
from rtpp_app.models.categorybudgets import CategoryBudget
from sqlalchemy.exc import ProgrammingError
from datetime import datetime
from rtpp_app.models.budgets import Budget
from sqlalchemy import func, case
from functools import wraps
from rtpp_app.models.invoice import Invoice

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    
    form = InvoiceForm()
    form.vendor.choices = [(v.id, v.vendor_name) for v in Vendor.query.all()]
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    categories = Category.query.all()  
    

    rows = (
        db.session.query(Category, CategoryBudget)
        .outerjoin(CategoryBudget, Category.id == CategoryBudget.category_id)
        .filter(Category.enabled.is_(True))
        .order_by(Category.name)
        .all()
    )

    budgets_data = [
        {
            "category_name": cat.name,
            "total_value": cb.total_value if cb else 0.0,
            "spent_value": cb.spent_value if cb else 0.0,
        }
        for cat, cb in rows
    ]

    return render_template(
        'dashboard.html',
        form=form,
        categories=categories,
        budgets=budgets_data
    )

@main_bp.route('/analytics')
@login_required
def analytics():

    start_date = request.args.get('start_date')
    end_date   = request.args.get('end_date')


    invoice_query = db.session.query(Invoice)


    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end   = datetime.strptime(end_date, "%Y-%m-%d")
            invoice_query = invoice_query.filter(Invoice.date_issue.between(start, end))
        except ValueError:
            pass

    invoices   = invoice_query.all()
    invoice_ids = [inv.id for inv in invoices]


    category_data = db.session.query(
        Category.name,
        func.coalesce(func.sum(Invoice.total_incl_vat), 0)
    ).outerjoin(Invoice, Invoice.category_id == Category.id) \
     .filter(Invoice.id.in_(invoice_ids)) \
     .group_by(Category.name).all()


    vendor_data = db.session.query(
        Vendor.vendor_name,
        func.coalesce(func.sum(Invoice.total_incl_vat), 0)
    ).join(Invoice, Invoice.vendor_id == Vendor.id) \
     .filter(Invoice.id.in_(invoice_ids)) \
     .group_by(Vendor.vendor_name).all()


    from sqlalchemy.orm import aliased
    InvoiceAlias = aliased(Invoice)
    budget_data = db.session.query(
        Category.name,
        func.coalesce(func.sum(InvoiceAlias.total_incl_vat), 0).label("total_spent"),
        Budget.total_budget
    ).join(Budget, Budget.category_id == Category.id) \
     .outerjoin(
         InvoiceAlias,
         (InvoiceAlias.category_id == Category.id) &
         (InvoiceAlias.id.in_(invoice_ids))
     ) \
     .group_by(Category.name, Budget.total_budget).all()

    return render_template(
        'analytics.html',
        category_data=category_data,
        vendor_data=vendor_data,
        budget_data=budget_data,
        start_date=start_date,
        end_date=end_date
    )
    return render_template('analytics.html')

