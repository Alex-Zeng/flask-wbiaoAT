"""empty message

Revision ID: 396762ccb7e5
Revises: 5a838508dbd6
Create Date: 2019-11-29 10:35:13.361746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '396762ccb7e5'
down_revision = '5a838508dbd6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('test_case', sa.Column('parent_directory', sa.Integer(), nullable=False, comment='父级目录ID'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('test_case', 'parent_directory')
    # ### end Alembic commands ###