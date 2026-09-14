"""Invoice header cleanup + category FK

Revision ID: 24d746bda1da
Revises: 7828f10e0b8e
Create Date: 2025-06-24 20:23:24.765701
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "24d746bda1da"
down_revision = "7828f10e0b8e"
branch_labels = None
depends_on = None


def upgrade():
    """
    1) **NIŠTA ne diramo** u tablici `budget`
       (ostavljamo FK category_id dok ne odlučiš drugačije).

    2) Dodajemo nove header-kolone – SVE privremeno `nullable=True`
       da bi postojeći redovi s NULL vrijednostima prošli.

    3) NE brišemo stare kolone (`firm_name`, `unit_price`…);
       to će ići u zasebnoj migraciji nakon što prebaciš podatke.
    """
    # --- nove kolone (sve nullable=True) ---------------------------
    #op.add_column("invoice", sa.Column("invoice_number", sa.String(100), nullable=True))
    #op.add_column("invoice", sa.Column("fiscal_number", sa.String(32), nullable=True))
    #op.add_column("invoice", sa.Column("order_number", sa.String(64), nullable=True))
    #op.add_column("invoice", sa.Column("date_issue", sa.Date(), nullable=True))
    #op.add_column("invoice", sa.Column("date_delivery", sa.Date(), nullable=True))
    #op.add_column("invoice", sa.Column("due_date", sa.Date(), nullable=True))
    #op.add_column("invoice", sa.Column("place_issue", sa.String(64), nullable=True))
    #op.add_column("invoice", sa.Column("payment_method", sa.String(32), nullable=True))
    #op.add_column("invoice", sa.Column("reference", sa.String(256), nullable=True))
    #op.add_column("invoice", sa.Column("updated_at", sa.DateTime(), nullable=True))
    sa.String()
    # vendor_id već postoji i ima vrijednosti → ne diramo NOT NULL
    # op.alter_column('invoice', 'vendor_id', existing_type=sa.INTEGER(), nullable=False)

    # --- stare kolone zadržavamo za kasniji data-migration ----------
    # (zakomentirano namjerno)
    #
    # op.drop_column('invoice', 'firm_name')
    # op.drop_column('invoice', 'date')
    # op.drop_column('invoice', 'iban')
    # op.drop_column('invoice', 'unit_price')
    # op.drop_column('invoice', 'account_number')
    # op.drop_column('invoice', 'bank_name')
    # op.drop_column('invoice', 'vat_number')
    # op.drop_column('invoice', 'vat_rate')
    # op.drop_column('invoice', 'updatedAt')
    # op.drop_column('invoice', 'photo_filename')
    # op.drop_column('invoice', 'quantity')


def downgrade():
    """
    Minimalni downgrade: makni nove kolone.
    (stare kolone su ionako ostale netaknute u upgrade-u)
    """
    op.drop_column("invoice", "updated_at")
    op.drop_column("invoice", "reference")
    op.drop_column("invoice", "payment_method")
    op.drop_column("invoice", "place_issue")
    op.drop_column("invoice", "due_date")
    op.drop_column("invoice", "date_delivery")
    op.drop_column("invoice", "date_issue")
    op.drop_column("invoice", "order_number")
    op.drop_column("invoice", "fiscal_number")
    op.drop_column("invoice", "invoice_number")
