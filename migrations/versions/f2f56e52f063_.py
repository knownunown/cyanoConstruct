"""empty message

Revision ID: f2f56e52f063
Revises: e102134316d4
Create Date: 2020-06-08 15:07:40.623608

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2f56e52f063'
down_revision = 'e102134316d4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE UserData SET googleAssoc = false WHERE googleAssoc IS NULL")
    op.alter_column('UserData', 'googleAssoc', nullable=False)
    return


def downgrade():
    op.alter_column('UserData', 'googleAssoc', nullable=True)
    return
