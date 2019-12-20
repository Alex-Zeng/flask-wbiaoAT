"""empty message

Revision ID: 1d5b3b032bce
Revises: 1b2c5be1e43f
Create Date: 2019-09-25 17:26:46.447460

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1d5b3b032bce'
down_revision = '1b2c5be1e43f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('equipment_management', sa.Column('setting_args', sa.Text(), nullable=True, comment='配置参数'))
    op.drop_column('equipment_management', 'appPackage')
    op.drop_column('equipment_management', 'automationName')
    op.drop_column('equipment_management', 'appActivity')
    op.drop_column('equipment_management', 'noReset')
    op.drop_column('equipment_management', 'dontStopAppOnRest')
    op.drop_column('equipment_management', 'platformVersion')
    op.drop_column('equipment_management', 'platformName')
    op.drop_column('equipment_management', 'systemPort')
    op.drop_column('equipment_management', 'deviceName')
    op.drop_column('equipment_management', 'autoGrantPermissions')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('equipment_management', sa.Column('autoGrantPermissions', mysql.VARCHAR(length=100), nullable=False, comment='自动确定您的应用需要哪些权限'))
    op.add_column('equipment_management', sa.Column('deviceName', mysql.VARCHAR(length=100), nullable=False, comment='使用的手机或模拟器类型'))
    op.add_column('equipment_management', sa.Column('systemPort', mysql.VARCHAR(length=100), nullable=False, comment='并发执行时需要用到'))
    op.add_column('equipment_management', sa.Column('platformName', mysql.VARCHAR(length=100), nullable=False, comment='使用的手机操作系统'))
    op.add_column('equipment_management', sa.Column('platformVersion', mysql.VARCHAR(length=100), nullable=False, comment='手机操作系统的版本'))
    op.add_column('equipment_management', sa.Column('dontStopAppOnRest', mysql.VARCHAR(length=100), nullable=False, comment='(仅安卓) 用于设置appium重启时是否先杀掉app'))
    op.add_column('equipment_management', sa.Column('noReset', mysql.VARCHAR(length=100), nullable=False, comment='在当前 session 下不会重置应用的状态。'))
    op.add_column('equipment_management', sa.Column('appActivity', mysql.VARCHAR(length=100), nullable=False, comment='启动页'))
    op.add_column('equipment_management', sa.Column('automationName', mysql.VARCHAR(length=100), nullable=False, comment='automationName'))
    op.add_column('equipment_management', sa.Column('appPackage', mysql.VARCHAR(length=100), nullable=False, comment='包名'))
    op.drop_column('equipment_management', 'setting_args')
    # ### end Alembic commands ###
