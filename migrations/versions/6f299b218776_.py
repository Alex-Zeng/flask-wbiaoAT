"""empty message

Revision ID: 6f299b218776
Revises: 1585d96b3260
Create Date: 2019-12-12 09:40:04.513075

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6f299b218776'
down_revision = '1585d96b3260'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('test_case_log', 'action_end_time',
               existing_type=mysql.DATETIME(),
               comment='测试步骤结束时间',
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('test_case_log', 'action_end_time',
               existing_type=mysql.DATETIME(),
               comment=None,
               existing_comment='测试步骤结束时间',
               existing_nullable=True)
    # ### end Alembic commands ###