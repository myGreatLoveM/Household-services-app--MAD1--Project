"""major changes

Revision ID: 51b70643c1c3
Revises: 06a5c84a6c59
Create Date: 2024-11-10 00:01:59.582561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51b70643c1c3'
down_revision = '06a5c84a6c59'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admin_escrows')
    op.drop_table('payout_requests')
    op.drop_table('provider_payouts')
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('short_description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('long_description', sa.Text(), nullable=True))
        batch_op.drop_column('description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.VARCHAR(length=100), nullable=True))
        batch_op.drop_column('long_description')
        batch_op.drop_column('short_description')

    op.create_table('provider_payouts',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('provider_id', sa.INTEGER(), nullable=False),
    sa.Column('total_earnings', sa.FLOAT(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('updated_at', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payout_requests',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('provider_id', sa.INTEGER(), nullable=False),
    sa.Column('amount', sa.FLOAT(), nullable=False),
    sa.Column('payout_cycle', sa.VARCHAR(length=20), nullable=True),
    sa.Column('status', sa.VARCHAR(length=20), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('updated_at', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('admin_escrows',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('escrow_balance', sa.FLOAT(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('updated_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###