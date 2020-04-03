"""empty message

Revision ID: 5591a8508127
Revises: fbf3052c319e
Create Date: 2020-02-28 15:20:24.999990

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5591a8508127'
down_revision = 'fbf3052c319e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('action', 'title')
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
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
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
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
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
    op.add_column('action', sa.Column('title', mysql.VARCHAR(length=100), nullable=False, comment='执行操作名称'))
    # ### end Alembic commands ###
