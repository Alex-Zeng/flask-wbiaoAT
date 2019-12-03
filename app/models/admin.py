from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from utils import create_browser_id
from flask import current_app
from itsdangerous import URLSafeSerializer
from ext import db


# 用户表
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telephone = db.Column(db.String(100), nullable=False, comment="手机号码")
    email = db.Column(db.String(100), nullable=False, comment="邮箱")
    username = db.Column(db.String(100), nullable=False, comment="用户名：登录用")
    password = db.Column(db.String(100), nullable=False, comment="密码")
    role = db.Column(db.String(100), comment="角色")
    status = db.Column(db.SmallInteger, nullable=False, default=1, comment="用户状态，0-禁用，1-启动")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")

    def __init__(self, *args, **kwargs):
        self.telephone = kwargs.get('telephone')
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.password = generate_password_hash(kwargs.get('password'))  # 加密密码
        self.role = kwargs.get('role')

    def __repr__(self):
        """Define the string format for instance of User."""
        return "<Model User `{}`>".format(self.username)

    def check_password(self, raw_password):
        result = check_password_hash(self.password, raw_password)
        return result

    def get_id(self, life_time=None):
        "生成token"
        key = current_app.config.get("SECRET_KEY", "The securet key by C~C!")  # current app 拿不到
        s = URLSafeSerializer(key)
        browser_id = create_browser_id()
        if not life_time:
            life_time = current_app.config.get("TOKEN_LIFETIME")
        token = s.dumps((self.id, self.username, self.password, browser_id, life_time))
        return token

# 项目表
class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="项目名")
    env_id = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment="项目名")
    is_del = db.Column(db.Integer, nullable=False, default=0, comment="是否已删除")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    author = db.relationship('User', backref=db.backref('project'))
    test_case = db.relationship('TestCase', backref=db.backref('project'))
    test_case_suit = db.relationship('TestCaseSuit', backref=db.backref('project'))
    page = db.relationship('Page', backref=db.backref('project'))