"""empty message

Revision ID: ca9f1e2babca
Revises: 
Create Date: 2019-08-16 15:53:09.402375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca9f1e2babca'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Function_info',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False, comment='方法名'),
    sa.Column('type', sa.String(length=100), nullable=True, comment='所属系统：通用，Android，IOS，PC'),
    sa.Column('description', sa.String(length=100), nullable=True, comment='方法说明'),
    sa.Column('create_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
    sa.Column('update_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False, comment='更新时间'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('telephone', sa.String(length=100), nullable=False, comment='手机号码'),
    sa.Column('email', sa.String(length=100), nullable=False, comment='邮箱'),
    sa.Column('username', sa.String(length=100), nullable=False, comment='用户名：登录用'),
    sa.Column('password', sa.String(length=100), nullable=False, comment='密码'),
    sa.Column('role', sa.String(length=100), nullable=True, comment='角色'),
    sa.Column('status', sa.SmallInteger(), nullable=False, comment='用户状态，0-禁用，1-启动'),
    sa.Column('create_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
    sa.Column('update_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False, comment='更新时间'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('project',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False, comment='项目名'),
    sa.Column('env_id', sa.Integer(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True, comment='项目名'),
    sa.Column('create_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
    sa.Column('update_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False, comment='更新时间'),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('page',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False, comment='页面名'),
    sa.Column('project_id', sa.Integer(), nullable=True, comment='项目id'),
    sa.Column('create_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
    sa.Column('update_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False, comment='更新时间'),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_case_suit',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False, comment='用例集名'),
    sa.Column('project_id', sa.Integer(), nullable=True, comment='所属项目ID'),
    sa.Column('description', sa.String(length=100), nullable=True, comment='说明'),
    sa.Column('create_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
    sa.Column('update_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False, comment='更新时间'),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('action',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False, comment='执行操作名称'),
    sa.Column('fun_id', sa.Integer(), nullable=False, comment='方法id'),
    sa.Column('ele_id', sa.Integer(), nullable=True, comment='所操作元素id'),
    sa.Column('page_id', sa.Integer(), nullable=True, comment='所属页面ID'),
    sa.Column('create_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
    sa.Column('update_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False, comment='更新时间'),
    sa.ForeignKeyConstraint(['page_id'], ['page.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('element',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False, comment='目录名'),
    sa.Column('type', sa.String(length=30), nullable=True, comment='查找方式'),
    sa.Column('loc', sa.String(length=200), nullable=True, comment='信息描述'),
    sa.Column('page_id', sa.Integer(), nullable=True, comment='所属页面ID'),
    sa.Column('create_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
    sa.Column('update_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False, comment='更新时间'),
    sa.ForeignKeyConstraint(['page_id'], ['page.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_case',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False, comment='用例名'),
    sa.Column('action_id', sa.Integer(), nullable=True, comment='用例步骤id，关联action表'),
    sa.Column('suit_id', sa.Integer(), nullable=True, comment='用例集id'),
    sa.Column('create_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
    sa.Column('update_datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False, comment='更新时间'),
    sa.ForeignKeyConstraint(['suit_id'], ['test_case_suit.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_case')
    op.drop_table('element')
    op.drop_table('action')
    op.drop_table('test_case_suit')
    op.drop_table('page')
    op.drop_table('project')
    op.drop_table('user')
    op.drop_table('Function_info')
    # ### end Alembic commands ###
