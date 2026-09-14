from rtpp_app import create_app, db
from rtpp_app.models.category import Category
from rtpp_app.models.categorybudgets import CategoryBudget
from rtpp_app.models.budgets import Budget
from rtpp_app.models.invoice import Invoice
from rtpp_app.models.invoiceitem import InvoiceItem
from rtpp_app.models.product import Product
from rtpp_app.models.vendor import Vendor
from rtpp_app.models.measuringunits import MeasuringUnit

def clear_test_data():
    """
    Delete all dummy data from tables except User.
    """
    models_to_clear = [
        InvoiceItem,
        Invoice,
        CategoryBudget,
        Budget,
        Product,
        Vendor,
        MeasuringUnit,
        Category
    ]

    # Bulk-delete every row from each table
    for model in models_to_clear:
        db.session.execute(model.__table__.delete())

    # Commit all deletions
    db.session.commit()
    print("✅ All test data cleared; users preserved.")

if __name__ == "__main__":
    # Create app context so that db and models are available
    app = create_app()
    with app.app_context():
        clear_test_data()
