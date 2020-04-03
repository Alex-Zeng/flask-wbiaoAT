"""empty message

Revision ID: db5bb9546759
Revises: e8cd95792a23
Create Date: 2019-12-19 10:14:13.012672

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'db5bb9546759'
down_revision = 'e8cd95792a23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('test_case_log', 'action_end_time',
               existing_type=mysql.TIMESTAMP(),
               comment='测试用例结束时间',
               existing_nullable=True)
    op.alter_column('test_case_log', 'action_start_time',
               existing_type=mysql.TIMESTAMP(),
               comment='测试用例开始时间',
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('test_case_suit_log', 'run_test_suit_end_time',
               existing_type=mysql.TIMESTAMP(),
               comment='测试集执行结束时间',
               existing_nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('test_case_suit_log', 'run_test_suit_start_time',
               existing_type=mysql.TIMESTAMP(),
               comment='测试集执行开始时间',
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('test_case_suit_log', 'run_test_suit_start_time',
               existing_type=mysql.TIMESTAMP(),
               comment=None,
               existing_comment='测试集执行开始时间',
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('test_case_suit_log', 'run_test_suit_end_time',
               existing_type=mysql.TIMESTAMP(),
               comment=None,
               existing_comment='测试集执行结束时间',
               existing_nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('test_case_log', 'action_start_time',
               existing_type=mysql.TIMESTAMP(),
               comment=None,
               existing_comment='测试用例开始时间',
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('test_case_log', 'action_end_time',
               existing_type=mysql.TIMESTAMP(),
               comment=None,
               existing_comment='测试用例结束时间',
               existing_nullable=True)
    # ### end Alembic commands ###
