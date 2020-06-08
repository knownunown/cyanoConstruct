"""empty message

Revision ID: e102134316d4
Revises: 9c5bf65fbb5e
Create Date: 2020-06-07 16:15:02.420281

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e102134316d4'
down_revision = 'bd2054290318'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('UserData', sa.Column('googleID', sa.TEXT(), nullable=True))
    op.add_column('UserData', sa.Column('googleAssoc', sa.BOOLEAN(), nullable=True))
    op.add_column('UserData', sa.Column('tempPass', sa.String(32), nullable = True))
    op.add_column('UserData', sa.Column('tempExp', sa.INTEGER(), nullable = True))
    return

def downgrade():
    op.drop_column('UserData', 'googleID')
    op.drop_column('UserData', 'googleAssoc')
    op.drop_column('UserData', 'tempPass')
    op.drop_column('UserData', 'tempExp')
    return
