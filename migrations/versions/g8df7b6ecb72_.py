"""empty message

Revision ID: g8df7b6ecb72
Revises: f2f56e52f063
Create Date: 2020-06-09 16:20:52.221567

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'g8df7b6ecb72'
down_revision = 'f2f56e52f063'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Backbone', sa.Column('desc', sa.String(length=128), nullable=False, server_default = "No description."))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Backbone', 'desc')
    # ### end Alembic commands ###
