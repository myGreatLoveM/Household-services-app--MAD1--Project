"""empty message

Revision ID: 0d8790c52c7a
Revises: 09cf5964f359
Create Date: 2024-11-10 17:59:09.530989

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d8790c52c7a'
down_revision = '09cf5964f359'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('providers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('approved_date', sa.DateTime(), nullable=True))

    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.add_column(sa.Column('approved_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.drop_column('approved_at')

    with op.batch_alter_table('providers', schema=None) as batch_op:
        batch_op.drop_column('approved_date')

    # ### end Alembic commands ###
