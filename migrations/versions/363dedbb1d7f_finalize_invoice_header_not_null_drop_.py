"""Finalize invoice header (NOT NULL + drop legacy)

Revision ID: 363dedbb1d7f
Revises: 24d746bda1da
Create Date: 2025-06-24 20:34:49.384349
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "363dedbb1d7f"
down_revision = "24d746bda1da"
branch_labels = None
depends_on = None


def upgrade():
    """1) učvrsti ključna nova polja kao NOT NULL
       2) obriši stare kolone iz invoice-a
    """

    # ---------- 1. NOT NULL ----------
    op.alter_column(
        "invoice",
        "invoice_number",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.alter_column(
        "invoice",
        "date_issue",
        existing_type=sa.Date(),
        nullable=False,
    )
    # updated_at ostaje nullable=True dok ne uvedemo automatsko popunjavanje

    # ---------- 2. DROP legacy ----------
    legacy_cols = [
        "firm_name",
        "iban",
        "unit_price",
        "account_number",
        "bank_name",
        "vat_number",
        "vat_rate",
        "updatedAt",
        "photo_filename",
        "quantity",
    ]
    for col in legacy_cols:
        op.drop_column("invoice", col)


def downgrade():
    """Vrati legacy kolone i dozvoli NULL na novim."""
    # 1) vrati stare kolone
    op.add_column("invoice", sa.Column("firm_name", sa.String(100), nullable=False))
    op.add_column("invoice", sa.Column("date", sa.Date(), nullable=False))
    op.add_column("invoice", sa.Column("iban", sa.String(64), nullable=True))
    op.add_column("invoice", sa.Column("unit_price", sa.Float(), nullable=False))
    op.add_column("invoice", sa.Column("account_number", sa.String(64), nullable=True))
    op.add_column("invoice", sa.Column("bank_name", sa.String(64), nullable=True))
    op.add_column("invoice", sa.Column("vat_number", sa.String(32), nullable=True))
    op.add_column("invoice", sa.Column("vat_rate", sa.Float(), nullable=False))
    op.add_column(
        "invoice", sa.Column("updatedAt", postgresql.TIMESTAMP(), nullable=False)
    )
    op.add_column(
        "invoice", sa.Column("photo_filename", sa.String(256), nullable=True)
    )
    op.add_column("invoice", sa.Column("quantity", sa.Integer(), nullable=False))

    # 2) ponovo dozvoli NULL
    op.alter_column(
        "invoice",
        "date_issue",
        existing_type=sa.Date(),
        nullable=True,
    )
    op.alter_column(
        "invoice",
        "invoice_number",
        existing_type=sa.String(length=100),
        nullable=True,
    )
