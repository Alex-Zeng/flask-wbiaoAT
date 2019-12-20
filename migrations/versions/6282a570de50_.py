"""empty message

Revision ID: 6282a570de50
Revises: b678076811fa
Create Date: 2019-10-10 11:31:44.501387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6282a570de50'
down_revision = 'b678076811fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test_args',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('test_case_id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=100), nullable=False, comment='参数名'),
    sa.Column('value', sa.Text(), nullable=True, comment='参数值'),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['test_case_id'], ['test_case.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_args')
    # ### end Alembic commands ###
