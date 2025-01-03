"""change in booking model

Revision ID: 152532d88099
Revises: 3eff95cc0e0b
Create Date: 2024-11-08 17:08:50.220056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '152532d88099'
down_revision = '3eff95cc0e0b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('book_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('fullfillment_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('confimation_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('completed_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('closed_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.drop_column('date_completed')
        batch_op.drop_column('date_booked')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_booked', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('date_completed', sa.DATETIME(), nullable=True))
        batch_op.drop_column('created_at')
        batch_op.drop_column('closed_date')
        batch_op.drop_column('completed_date')
        batch_op.drop_column('confimation_date')
        batch_op.drop_column('fullfillment_date')
        batch_op.drop_column('book_date')

    # ### end Alembic commands ###
