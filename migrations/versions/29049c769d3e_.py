"""empty message

Revision ID: 29049c769d3e
Revises: 4b7d541ef71d
Create Date: 2024-11-05 17:10:53.115632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29049c769d3e'
down_revision = '4b7d541ef71d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.drop_column('date_scheduled')

    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('service_cost', sa.Integer(), nullable=False))
        batch_op.alter_column('method',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=20),
               nullable=True)
        batch_op.drop_column('total_amount')
        batch_op.drop_column('service_price')
        batch_op.drop_column('tax')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tax', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('service_price', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('total_amount', sa.INTEGER(), nullable=False))
        batch_op.alter_column('method',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.drop_column('service_cost')

    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_scheduled', sa.DATETIME(), nullable=True))

    # ### end Alembic commands ###
