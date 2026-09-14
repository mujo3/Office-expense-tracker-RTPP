import os
import re
from datetime import date, datetime

from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    current_app, abort, request, jsonify
)
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from PIL import Image
import pytesseract
from invoice2data import extract_data
from rtpp_app.extensions import db, login_manager, csrf
from rtpp_app.forms import InvoiceForm
from rtpp_app.models.vendor import Vendor
from rtpp_app.models.category import Category
from rtpp_app.models.product import Product
from rtpp_app.models.measuringunits import MeasuringUnit
from rtpp_app.models.categorybudgets import CategoryBudget
from rtpp_app.models.invoice import Invoice
from rtpp_app.models.invoiceitem import InvoiceItem


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



#OCR Vendor dropdown menu picker
def vendor_from_text(txt: str) -> str:
    lowered = txt.lower()
    for v in Vendor.query.all():
        if v.vendor_name.lower() in lowered:
            return v.vendor_name
    return ""


def parse_invoice(img_path: str) -> dict:

    try:
        data = extract_data(img_path) or {}
    except Exception:
        data = {}

    if not data:
        text = pytesseract.image_to_string(Image.open(img_path), lang="bos+eng")
        current_app.logger.debug("OCR TEXT ->\n%s\n<- END", text)

        inv_no = re.search(r"Racun\s+broj[:\s]*([0-9\- ]+)", text, re.I)
        inv_no = inv_no.group(1).replace(" ", "") if inv_no else ""

        fiscal = (re.search(r"Fiskalni\s+racun[i]?\s*[:\-]?\s*(\d{2,})", text, re.I)
                  or re.search(r"^\s*(\d{4,6})\s+Ul\.", text, re.M))

        place  = re.search(r"mjesto\s+izdavanja[:\s]*([A-Za-zĆČŽŠĐ.\- ]+)", text, re.I)
        paym   = re.search(r"Nacin\s+placanja[:\s]*([A-Za-zĆČŽŠĐ.\- ]+)", text, re.I)

        dates = re.findall(r"(\d{2}\.\d{2}\.\d{4})", text)
        date_issue, date_delivery, due_date = (dates + ["", "", ""])[:3]

        total_ex = re.search(r"Ukupno\s+KM[:\s]*([0-9\.,]+)", text, re.I)
        vat_amt  = re.search(r"Iznos\s+PDV[-a]*[:\s]*([0-9\.,]+)", text, re.I)

        items = []
        row_pat = re.compile(
            r"""
            (?P<code>\d{3,})
            .*?
            (?P<name>[A-Z0-9 ĆČŽŠĐa-z\-% ]+?)\s+Pak:   # naziv do "Pak:"
            .*?\s(?P<unit>KOM|KG|L|M|KOMADA)\s+
            (?P<extra>[0-9,.\s]{10,})$
            """,
            re.X | re.M | re.S
        )

        for m in row_pat.finditer(text):
            code = m.group('code')
            name = m.group('name').strip()
            unit = m.group('unit').upper()


            nums = re.findall(r"[0-9]+,[0-9]{2,4}", m.group('extra'))
            if len(nums) < 2:
                continue
            price = nums[1].replace(",", ".") if len(nums) > 1 else "0"

            qty_match = re.search(r"\b(\d{1,5})\b", m.group('extra'))
            qty = int(qty_match.group(1)) if qty_match else 0

            items.append({
                "product_code": code,
                "product_name": name,
                "measuring_unit": unit,
                "unit_price_excl_vat": price,
                "quantity": qty,
                "vat_rate": 17.0
            })

        current_app.logger.debug("PARSED %d items", len(items))


        data = {
            "invoice_number":    inv_no,
            "fiscal_receipt_no": fiscal.group(1) if fiscal else "",
            "date_issue":        date_issue,
            "date_delivery":     date_delivery,
            "due_date":          due_date,
            "place_issue":       place.group(1).strip() if place else "",
            "payment_method":    paym.group(1).strip() if paym else "",
            "vendor_name":       vendor_from_text(text),
            "total_excl_vat":    (total_ex.group(1).replace(".", "").replace(",", ".") if total_ex else ""),
            "vat_amount":        (vat_amt.group(1).replace(".", "").replace(",", ".") if vat_amt else ""),
            "items":             items,
        }
    return data



expenses_bp = Blueprint(
    "expenses", __name__,
    template_folder="templates",
    url_prefix="/expenses",
)

@csrf.exempt
@expenses_bp.route("/invoice-ocr", methods=["POST"])
def invoice_ocr():
    if "photo" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["photo"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    tmp_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "tmp", filename)
    os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
    file.save(tmp_path)

    try:
        data = parse_invoice(tmp_path)
        return jsonify(data), 200
    except Exception as err:
        current_app.logger.exception("OCR parse failed")
        return jsonify({"error": str(err)}), 500
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def roles_required(*roles):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            role = (getattr(current_user, "user_role", None)
                    or getattr(current_user, "role", None))
            if role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator



@expenses_bp.route("/invoice-entry", methods=["GET", "POST"])
@login_required
@roles_required("admin", "employee")
def invoice_entry():
    form = InvoiceForm()


    vendors = Vendor.query.order_by(Vendor.vendor_name).all()
    form.vendor.choices = [(v.id, v.vendor_name) for v in vendors]

    categories = Category.query.filter_by(enabled=True).order_by(Category.name).all()
    form.category.choices = [(c.id, c.name) for c in categories]


    units = MeasuringUnit.query.order_by(MeasuringUnit.id).all()
    products = Product.query.order_by(Product.item_name).all()


    recent_invoices = Invoice.query.order_by(Invoice.id.desc()).limit(8).all()
    categories_filter = Category.query.order_by(Category.name).all()

    cat_budgets = CategoryBudget.query.all()
    budgets_data = [
        {
            "category_name": cb.category.name,
            "total_value": cb.total_value,
            "spent_value": cb.spent_value,
        }
        for cb in cat_budgets
    ]


    context = {
        "form": form,
        "budgets": budgets_data,
        "all_vendors": vendors,
        "all_categories": categories,
        "recent_invoices": recent_invoices,
        "categories_filter": categories_filter,
        "all_units": units,
        "all_products": products,
    }


    if request.method == "POST":


        if "new_vendor_name" in request.form:
            name = request.form.get("new_vendor_name", "").strip()
            if not name:
                flash("Vendor name is required.", "danger")
                return redirect(url_for("expenses.invoice_entry"))

            v = Vendor(
                vendor_name=name,
                vat_number=request.form.get("new_vendor_pdv", "").strip(),
                account_number=request.form.get("new_vendor_account", "").strip(),
                bank=request.form.get("new_vendor_bank", "").strip(),
                adress=request.form.get("new_vendor_address", "").strip(),
                vendorCity=request.form.get("new_vendor_city", "").strip(),
                vendorTelephone=request.form.get("new_vendor_telephone", "").strip(),
                vendorEmail=request.form.get("new_vendor_email", "").strip(),
                vendorTransact=request.form.get("new_vendor_transact", "").strip(),
                supportsAvans=request.form.get("new_vendor_supports_avans") == "on",
            )
            db.session.add(v)
            db.session.commit()
            flash(f'Vendor "{name}" added.', "success")
            return redirect(url_for("expenses.invoice_entry"))


        if "new_product_name" in request.form:
            pname = request.form.get("new_product_name", "").strip()
            try:
                cat_id = int(request.form.get("new_product_category_id", ""))
            except ValueError:
                cat_id = None
            unit_text = request.form.get("new_product_unit_text", "").strip()

            if not (pname and cat_id and unit_text):
                flash("Product name, category and measuring unit are required.", "danger")
                return redirect(url_for("expenses.invoice_entry"))

            cat_obj = Category.query.get(cat_id)
            if not cat_obj:
                flash("Invalid category.", "danger")
                return redirect(url_for("expenses.invoice_entry"))

            unit_obj = MeasuringUnit.query.filter_by(measuring_unit=unit_text).first()
            if not unit_obj:
                unit_obj = MeasuringUnit(
                    id=unit_text.lower().replace(" ", "_"),
                    measuring_unit=unit_text,
                )
                db.session.add(unit_obj)
                db.session.commit()

            p = Product(
                item_name=pname,
                category_id=cat_id,
                measuring_units_id=unit_obj.id,
            )
            db.session.add(p)
            db.session.commit()
            flash(f'Product "{pname}" added.', "success")
            return redirect(url_for("expenses.invoice_entry"))


        if form.validate_on_submit():


            names       = request.form.getlist("product_name[]")
            units_in    = request.form.getlist("measuring_unit[]")
            codes       = request.form.getlist("product_code[]")
            quantities  = request.form.getlist("quantity[]")
            prices_ex   = request.form.getlist("unit_price_excl_vat[]")
            vat_rates   = request.form.getlist("vat_rate[]")
            discounts   = request.form.getlist("discount[]")

            items = []
            for idx, raw_name in enumerate(names):
                name = raw_name.strip()
                if not name:
                    continue


                mu = units_in[idx].strip()
                if not mu:
                    flash(f"Measuring unit required at row {idx+1}", "danger")
                    return render_template("dashboard.html", **context)


                try:
                    qty = int(quantities[idx])
                    if qty <= 0:
                        raise ValueError
                except ValueError:
                    flash(f"Invalid quantity at row {idx+1}", "danger")
                    return render_template("dashboard.html", **context)


                try:
                    price = float(prices_ex[idx])
                    if price < 0:
                        raise ValueError
                except ValueError:
                    flash(f"Invalid unit price at row {idx+1}", "danger")
                    return render_template("dashboard.html", **context)


                try:
                    vat_r = float(vat_rates[idx])
                    if vat_r < 0:
                        raise ValueError
                except ValueError:
                    flash(f"Invalid VAT rate at row {idx+1}", "danger")
                    return render_template("dashboard.html", **context)


                try:
                    disc_raw = discounts[idx] if idx < len(discounts) else ""
                    disc     = float(disc_raw) if disc_raw else 0.0
                    if disc < 0:
                        raise ValueError
                except ValueError:
                    flash(f"Invalid discount at row {idx+1}", "danger")
                    return render_template("dashboard.html", **context)

                items.append(
                    {
                        "product_name":          name,
                        "measuring_unit":        mu,
                        "product_code":          codes[idx].strip() or None,
                        "quantity":              qty,
                        "unit_price_excl_vat":   price,
                        "vat_rate":              vat_r,
                        "discount":              disc,
                    }
                )


            if not items:
                flash("At least one valid line item is required.", "danger")
                return render_template("dashboard.html", **context)


            filename = None
            if form.photo.data:
                original = secure_filename(form.photo.data.filename)
                filename = f"{date.today():%Y%m%d}_{original}"
                storage  = current_app.config.get("UPLOAD_FOLDER", "uploads")
                dst      = os.path.join(storage, filename)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                form.photo.data.save(dst)


            total_qty     = 0
            total_excl    = 0.0
            total_vat_amt = 0.0

            for it in items:
                line_net = max(
                    0.0,
                    it["quantity"] * it["unit_price_excl_vat"] - it["discount"]
                )
                line_vat = line_net * (it["vat_rate"] / 100.0)

                total_qty     += it["quantity"]
                total_excl    += line_net
                total_vat_amt += line_vat

            total_incl = total_excl + total_vat_amt


            inv = Invoice(
                invoice_number = form.invoice_number.data.strip(),
                fiscal_number  = form.fiscal_number.data.strip() or None,
                order_number   = form.order_number.data.strip() or None,
                date_issue     = form.date_of_issue.data,
                date_delivery  = form.date_of_delivery.data or None,
                due_date       = form.due_date.data or None,
                place_issue    = form.place_of_issue.data.strip() or None,
                payment_method = form.payment_method.data,
                reference      = form.reference.data.strip() or None,
                vendor_id      = form.vendor.data,
                category_id    = form.category.data,
                total_excl_vat = total_excl,
                vat_amount     = total_vat_amt,
                total_incl_vat = total_incl,
                created_at     = datetime.utcnow(),
                updated_at     = datetime.utcnow(),
            )
            db.session.add(inv)
            db.session.flush()


            for it in items:
                line_net = max(
                    0.0,
                    it["quantity"] * it["unit_price_excl_vat"] - it["discount"]
                )
                line_vat = line_net * (it["vat_rate"] / 100.0)
                line_inc = line_net + line_vat

                ii = InvoiceItem(
                    invoice_id            = inv.id,
                    item_name             = it["product_name"],
                    measuring_unit        = it["measuring_unit"],
                    product_code          = it["product_code"],
                    quantity              = it["quantity"],
                    unit_price_excl_vat   = it["unit_price_excl_vat"],
                    unit_price_incl_vat   = it["unit_price_excl_vat"] * (1 + it["vat_rate"] / 100.0),
                    total_excl_vat        = line_net,
                    vat_rate              = it["vat_rate"],
                    vat_amount            = line_vat,
                    total_incl_vat        = line_inc,
                    discount              = it["discount"],
                )
                db.session.add(ii)


            cb = CategoryBudget.query.filter_by(category_id=form.category.data).first()
            if cb:
                cb.spent_value = (cb.spent_value or 0.0) + total_excl

            db.session.commit()
            flash("Invoice recorded successfully.", "success")
            return redirect(url_for("expenses.invoice_entry"))


        flash("Form validation failed. Check required fields.", "danger")


    return render_template("dashboard.html", **context)
