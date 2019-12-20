"""empty message

Revision ID: d689a7069563
Revises: 5e763f2aa2c2
Create Date: 2019-12-18 18:08:46.095349

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd689a7069563'
down_revision = '5e763f2aa2c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('test_case_log', 'action_end_time',
               existing_type=mysql.DATETIME(),
               comment='测试用例结束时间',
               existing_nullable=True)
    op.alter_column('test_case_log', 'action_start_time',
               existing_type=mysql.DATETIME(),
               comment='测试用例开始时间',
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('test_case_suit_log', 'run_test_suit_end_time',
               existing_type=mysql.DATETIME(),
               comment='测试集执行结束时间',
               existing_nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    op.alter_column('test_case_suit_log', 'run_test_suit_start_time',
               existing_type=mysql.DATETIME(),
               comment='测试集执行开始时间',
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('test_case_suit_log', 'run_test_suit_start_time',
               existing_type=mysql.DATETIME(),
               comment=None,
               existing_comment='测试集执行开始时间',
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('test_case_suit_log', 'run_test_suit_end_time',
               existing_type=mysql.DATETIME(),
               comment=None,
               existing_comment='测试集执行结束时间',
               existing_nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    op.alter_column('test_case_log', 'action_start_time',
               existing_type=mysql.DATETIME(),
               comment=None,
               existing_comment='测试用例开始时间',
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('test_case_log', 'action_end_time',
               existing_type=mysql.DATETIME(),
               comment=None,
               existing_comment='测试用例结束时间',
               existing_nullable=True)
    # ### end Alembic commands ###