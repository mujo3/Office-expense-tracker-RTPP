"""Added period and recurring budget to CategoryBudget

Revision ID: e29edc643630
Revises: 0f51646da571
Create Date: 2025-06-25 01:49:01.536288

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'e29edc643630'
down_revision = '0f51646da571'
branch_labels = None
depends_on = None


def upgrade():

    #op.add_column(
        #'category_budgets',
        #sa.Column(
         #   'year',
        #    sa.Integer(),
       #     nullable=True,
      #      server_default=sa.text(str(datetime.utcnow().year))
     #   )
    #)
    #op.execute(
     #   "UPDATE category_budgets "
      #  "SET year = EXTRACT(YEAR FROM created_at)::integer "
       # "WHERE year IS NULL"
    #)
    #op.alter_column(
     #   'category_budgets',
      #  'year',
       # existing_type=sa.Integer(),
        #nullable=False,
        #server_default=None
    #)


    #op.add_column(
     #   'category_budgets',
      #  sa.Column(
       #     'month',
        #    sa.Integer(),
         #   nullable=True,
          #  server_default=sa.text(str(datetime.utcnow().month))
        #)
    #)
    #op.execute(
     #   "UPDATE category_budgets "
      #  "SET month = EXTRACT(MONTH FROM created_at)::integer "
       # "WHERE month IS NULL"
    #)
    #op.alter_column(
     #   'category_budgets',
     #   'month',
      #  existing_type=sa.Integer(),
       # nullable=False,
        #server_default=None
    #)


    #op.add_column(
     #   'category_budgets',
      #  sa.Column(
       #     'recurring',
        #    sa.Boolean(),
         #   nullable=True,
          #  server_default=sa.false()
        #)
    #)
    #op.execute(
     #   "UPDATE category_budgets "
      #  "SET recurring = FALSE "
       # "WHERE recurring IS NULL"
    #)
    #op.alter_column(
     #   'category_budgets',
      #  'recurring',
       # existing_type=sa.Boolean(),
        #nullable=False,
        #server_default=None
    #)
    sa.String()


def downgrade():

    op.drop_column('category_budgets', 'recurring')
    op.drop_column('category_budgets', 'month')
    op.drop_column('category_budgets', 'year')
