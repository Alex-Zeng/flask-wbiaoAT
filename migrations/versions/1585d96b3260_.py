"""empty message

Revision ID: 1585d96b3260
Revises: 29af66db1096
Create Date: 2019-12-11 17:16:27.222352

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1585d96b3260'
down_revision = '29af66db1096'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('equipment_management', sa.Column('cron_status', sa.Integer(), nullable=False, comment='定时任务状态 0停止,1启动'))
    op.add_column('equipment_management', sa.Column('cron_times', sa.String(length=100), nullable=True, comment='crontab表达式'))
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
    op.drop_column('equipment_management', 'cron_times')
    op.drop_column('equipment_management', 'cron_status')
    # ### end Alembic commands ###