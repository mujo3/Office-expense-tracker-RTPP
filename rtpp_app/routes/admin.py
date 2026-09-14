from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, logout_user
from rtpp_app.extensions import db
from rtpp_app.models.user import User
from rtpp_app.models.category import Category
from rtpp_app.models.categorybudgets import CategoryBudget
from sqlalchemy import text
from datetime import date

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def index():
    return redirect(url_for('admin.users'))

@admin_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash("You do not have access to this page.", "danger")
        return redirect(url_for('main.dashboard'))
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/categories')
@login_required
def categories():
    if not current_user.is_admin:
        flash("You do not have access to this page.", "danger")
        return redirect(url_for('main.dashboard'))
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

from sqlalchemy.exc import ProgrammingError

@admin_bp.route('/budgets')
@login_required
def budgets():
    if not current_user.is_admin:
        flash("You do not have access to this page.", "danger")
        return redirect(url_for('main.dashboard'))

    # Auto-clone next month for recurring budgets
    today = date.today()
    next_month = today.month % 12 + 1
    next_year = today.year + (1 if today.month == 12 else 0)

    recurring = CategoryBudget.query.filter_by(
        recurring=True,
        month=today.month,
        year=today.year
    ).all()
    for rb in recurring:
        exists = CategoryBudget.query.filter_by(
            category_id=rb.category_id,
            month=next_month,
            year=next_year
        ).first()
        if not exists:
            clone = CategoryBudget(
                category_id=rb.category_id,
                total_value=rb.total_value,
                spent_value=0.0,
                month=next_month,
                year=next_year,
                recurring=True
            )
            db.session.add(clone)
    db.session.commit()

    categories = Category.query.all()
    budgets = CategoryBudget.query.order_by(
        CategoryBudget.year.desc(),
        CategoryBudget.month.desc()
    ).all()

    return render_template(
        'admin/budgets.html',
        categories=categories,
        budgets=budgets,
        current_year=today.year,
        current_month=today.month
    )


@admin_bp.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash("You do not have permission.", "danger")
        return redirect(url_for('admin.users'))

    first_name = request.form.get('firstName')
    last_name  = request.form.get('lastName')
    email      = request.form.get('email')
    role       = request.form.get('role')

    if not all([first_name, last_name, email, role]):
        flash("All fields are required.", "danger")
        return redirect(url_for('admin.users'))

    if User.query.filter_by(email=email).first():
        flash("User already exists.", "warning")
        return redirect(url_for('admin.users'))

    try:
        new_user = User(
            firstName=first_name,
            lastName=last_name,
            email=email,
            role=role,
            reset_password_link=""
        )
        new_user.set_password('htecoffice')
        db.session.add(new_user)
        db.session.commit()
        flash("User added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding user: {str(e)}", "danger")

    return redirect(url_for('admin.users'))


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("You do not have permission.", "danger")
        return redirect(url_for('admin.users'))
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "danger")
    return redirect(url_for('admin.users'))

@admin_bp.route('/add_category', methods=['POST'])
@login_required
def add_category():
    if not current_user.is_admin:
        flash("You do not have permission.", "danger")
        return redirect(url_for('admin.categories'))
    name = request.form.get('name')
    if not name:
        flash("Category name is required.", "danger")
        return redirect(url_for('admin.categories'))
    if Category.query.filter_by(name=name).first():
        flash("Category already exists.", "warning")
        return redirect(url_for('admin.categories'))
    try:
        cat = Category(name=name, enabled=True)
        db.session.add(cat)
        db.session.commit()
        flash("Category added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding category: {str(e)}", "danger")
    return redirect(url_for('admin.categories'))


@admin_bp.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    if not current_user.is_admin:
        flash("You do not have permission.", "danger")
        return redirect(url_for('admin.budgets'))

    cid       = request.form.get('category_id')
    amt       = request.form.get('amount')
    year      = request.form.get('year')
    month     = request.form.get('month')
    recurring = (request.form.get('recurring') == 'on')

    if not all([cid, amt, year, month]):
        flash("All fields are required.", "danger")
        return redirect(url_for('admin.budgets'))

    try:
        amt   = float(amt)
        year  = int(year)
        month = int(month)

        budget = CategoryBudget.query.filter_by(
            category_id=cid,
            year=year,
            month=month
        ).first()

        if budget:
            budget.total_value = amt
            budget.recurring   = recurring
        else:
            budget = CategoryBudget(
                category_id=cid,
                total_value=amt,
                spent_value=0.0,
                year=year,
                month=month,
                recurring=recurring
            )
            db.session.add(budget)

        db.session.commit()
        flash("Budget updated successfully.", "success")

    except ValueError:
        flash("Invalid input.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error setting budget: {e}", "danger")

    return redirect(url_for('admin.budgets'))

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

@admin_bp.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        flash("You do not have permission.", "danger")
        return redirect(url_for('admin.categories'))


    try:
        db.session.execute(
            text("DELETE FROM category_budgets WHERE category_id = :cid"),
            {"cid": category_id}
        )
        db.session.commit()
    except Exception:

        db.session.rollback()


    try:
        db.session.execute(
            text("DELETE FROM category WHERE id = :cid"),
            {"cid": category_id}
        )
        db.session.commit()
        flash("Category deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting category: {str(e)}", "danger")

    return redirect(url_for('admin.categories'))

@admin_bp.route('/edit_budget/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    if not current_user.is_admin:
        flash("You do not have permission.", "danger")
        return redirect(url_for('admin.budgets'))

    budget = CategoryBudget.query.get_or_404(budget_id)

    if request.method == 'POST':
        new_amount = request.form.get('amount')
        try:
            budget.total_value = float(new_amount)
            db.session.commit()
            flash("Budget updated.", "success")
            return redirect(url_for('admin.budgets'))
        except ValueError:
            flash("Invalid amount.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating budget: {str(e)}", "danger")

    return render_template('admin/edit_budget.html', budget=budget)
