"""Dodavanje novih tabela blacklist_tokens, category_budgets, budgets, invoice_items i measuring_units, te nadogradnja prethodno postojećih baza

Revision ID: 1f6d192512cb
Revises: 2c30c2eb291a
Create Date: 2025-05-28 00:23:27.542765
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, select
from sqlalchemy import String, Integer, Float, DateTime, Boolean, Date
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '1f6d192512cb'
down_revision = '2c30c2eb291a'
branch_labels = None
depends_on = None


def upgrade():
    now = datetime.utcnow()
    
    #op.execute('DROP TABLE measuring_units CASCADE')

    op.create_table(
        'blacklist_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('token', sa.String(length=200), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )

    op.create_table(
        'budgets',
        sa.Column('id', sa.String(length=20), primary_key=True),
        sa.Column('total_budget', sa.Float(), nullable=False),
        sa.Column('spent_budget', sa.Float(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    

    op.create_table(
        'measuring_units',
        sa.Column('id', sa.String(length=20), primary_key=True),
        sa.Column('measuring_unit', sa.String(length=15), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )

    #op.create_table(
     #   'category_budgets',
      #  sa.Column('id', sa.Integer, primary_key=True),
      #  sa.Column('category_id', sa.Integer, nullable=False),
      #  sa.Column('budget_id', sa.String(length=20), nullable=False),
      #  sa.Column('total_value', sa.Float(), nullable=False),
      #  sa.Column('spent_value', sa.Float(), nullable=False),
      #  sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
      #  sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
      #  sa.ForeignKeyConstraint(['budget_id'], ['budgets.id']),
      #  sa.ForeignKeyConstraint(['category_id'], ['category.id'])
    #)

    #op.create_table(
     #   'invoice_items',
     #   sa.Column('invoice_item_id', sa.Integer(), primary_key=True),
     #   sa.Column('invoice_id', sa.Integer(), nullable=True),
     #   sa.Column('product_id', sa.Integer(), nullable=True),
     #   sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
     #   sa.Column('unit_price_excl_vat', sa.Float(), nullable=False, server_default='0'),
     #   sa.Column('unit_price_incl_vat', sa.Float(), nullable=False, server_default='0'),
     #   sa.Column('total_excl_vat', sa.Float(), nullable=False, server_default='0'),
     #   sa.Column('total_incl_vat', sa.Float(), nullable=False, server_default='0'),
     #   sa.Column('discount', sa.Float(), nullable=False, server_default='0'),
     #   sa.Column('vat_rate', sa.Float(), nullable=False, server_default='0'),
     #   sa.Column('vat_amount', sa.Float(), nullable=False, server_default='0'),
     #   sa.Column('product_code', sa.String(), nullable=True),
     #   sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
     #   sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
     #   sa.ForeignKeyConstraint(['invoice_id'], ['invoice.id']),
      #  sa.ForeignKeyConstraint(['product_id'], ['products.id'])
    #)


    connection = op.get_bind()


    invoice_product_table = table('invoice_product',
        column('invoice_id', Integer),
        column('product_id', Integer)
    )


    result = connection.execute(select(
        invoice_product_table.c.invoice_id,
        invoice_product_table.c.product_id
    )).fetchall()

    for row in result:
        connection.execute(
            sa.text("""
                INSERT INTO invoice_items (
                    invoice_id, product_id, quantity,
                    unit_price_excl_vat, unit_price_incl_vat,
                    total_excl_vat, total_incl_vat,
                    discount, vat_rate, vat_amount,
                    created_at, updated_at
                ) VALUES (
                    :invoice_id, :product_id, 1,
                    0, 0,
                    0, 0,
                    0, 0, 0,
                    :now, :now
                )
            """),
            {
                'invoice_id': row.invoice_id,
                'product_id': row.product_id,
                'now': now
            }
        )


    op.drop_table('invoice_product')


    with op.batch_alter_table('category') as batch_op:
        #batch_op.add_column(sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'))
        sa.String()
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))


    with op.batch_alter_table('invoice') as batch_op:
        #batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        #batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        #batch_op.alter_column('date', type_=sa.Date(), postgresql_using='date::date', existing_nullable=False)
        #batch_op.alter_column('vat_number', type_=sa.String(length=32), existing_nullable=True)
        #batch_op.alter_column('account_number', type_=sa.String(length=64), existing_nullable=True)
        #batch_op.alter_column('iban', type_=sa.String(length=64), existing_nullable=True)
        #batch_op.alter_column('bank_name', type_=sa.String(length=64), existing_nullable=True)
        #batch_op.alter_column('unit_price', type_=sa.Float(), existing_nullable=False)
        #batch_op.alter_column('photo_filename', type_=sa.String(length=256), existing_nullable=True)
        #batch_op.alter_column('vendor_id', existing_nullable=True)
        #batch_op.drop_constraint('invoice_vat_number_key', type_='unique')
        #batch_op.drop_column('firm_adress')
        sa.String()


    with op.batch_alter_table('products') as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        batch_op.add_column(sa.Column('measuring_unit_id', sa.String(length=20), nullable=True))
        batch_op.create_foreign_key('fk_products_measuring_unit_id', 'measuring_units', ['measuring_unit_id'], ['id'])
        #batch_op.drop_column('price')
        #batch_op.drop_column('unit_price')
        #batch_op.drop_column('quantity')
        #batch_op.drop_column('total_excl_vat')


    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('first_name', sa.String(), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('last_name', sa.String(), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        #batch_op.add_column(sa.Column('reset_password_link', sa.String(), nullable=False, server_default=''))


    with op.batch_alter_table('vendor') as batch_op:
        batch_op.add_column(sa.Column('vendor_city', sa.String(length=50), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('vendor_telephone', sa.String(length=20), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('vendor_email', sa.String(length=100), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('vendor_transact', sa.String(length=100), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('supports_avans', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))


def downgrade():

    op.drop_table('invoice_items')
    op.drop_table('category_budgets')
    op.drop_table('measuring_units')
    op.drop_table('budgets')
    op.drop_table('blacklist_tokens')

    with op.batch_alter_table('vendor') as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('supports_avans')
        batch_op.drop_column('vendor_transact')
        batch_op.drop_column('vendor_email')
        batch_op.drop_column('vendor_telephone')
        batch_op.drop_column('vendor_city')

    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('reset_password_link')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')

    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_constraint('fk_products_measuring_unit_id', type_='foreignkey')
        batch_op.drop_column('measuring_unit_id')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.add_column(sa.Column('price', sa.Float(), nullable=False))
        batch_op.add_column(sa.Column('unit_price', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('quantity', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('total_excl_vat', sa.Float(), nullable=False))

    with op.batch_alter_table('invoice') as batch_op:
        batch_op.add_column(sa.Column('firm_adress', sa.String(length=200), nullable=False))
        batch_op.create_unique_constraint('invoice_vat_number_key', ['vat_number'])
        batch_op.alter_column('vendor_id', nullable=False)
        batch_op.alter_column('photo_filename', type_=sa.String(length=20), nullable=False)
        batch_op.alter_column('unit_price', type_=sa.Integer(), nullable=False)
        batch_op.alter_column('bank_name', type_=sa.String(length=100), nullable=False)
        batch_op.alter_column('iban', type_=sa.String(length=20), nullable=False)
        batch_op.alter_column('account_number', type_=sa.String(length=50), nullable=False)
        batch_op.alter_column('vat_number', type_=sa.String(length=20), nullable=False)
        batch_op.alter_column('date', type_=sa.String(length=10), nullable=False)
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')

    with op.batch_alter_table('category') as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('enabled')

    op.create_table(
        'invoice_product',
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoice.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('invoice_id', 'product_id')
    )
