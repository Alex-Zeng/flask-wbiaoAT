from flask import jsonify, request, session, current_app
from app.models.admin import User, Project
from ext import db, simple_cache
from flask_login import login_user, login_required, logout_user
from app.models import user_loader
from flask_restful import Resource, reqparse

parser_register = reqparse.RequestParser()
parser_register.add_argument('telephone', type=str, required=True, help="telephone cannot be blank!")
parser_register.add_argument('username', type=str, required=True, help="username cannot be blank!")
parser_register.add_argument('email', type=str, required=True, help="username cannot be blank!")
parser_register.add_argument('password1', type=str, required=True, help="password1 cannot be blank!")
parser_register.add_argument('password2', type=str, required=True, help="password2 cannot be blank!")


class Register(Resource):

    def post(self):
        args = parser_register.parse_args()
        telephone = args.get('telephone')  # 不开放注册,暂时只能自己用
        username = args.get('username')
        email = args.get('email')
        password1 = args.get('password1')
        password2 = args.get('password2')

        if User.query.filter(User.telephone == telephone).first():
            return jsonify({'status': '0', 'data': {}, 'msg': '该手机号码已被注册!'})

        if User.query.filter(User.username == username).first():
            return jsonify({'status': '0', 'data': {}, 'msg': '该用户名已被使用!'})

        if password1 != password2:
            return jsonify({'status': '0', 'data': {}, 'msg': '两次输入的密码不相同,请核对后再次提交!'})

        user1 = User(telephone=telephone, username=username, password=password1, email=email)
        db.session.add(user1)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'msg': '注册成功'})


parser_login = reqparse.RequestParser()
# 必需的参数:要求一个值传递的参数，只需要添加 required=True 来调用 add_argument()
parser_login.add_argument('username', type=str, required=True, help="username cannot be blank!", )
parser_login.add_argument('password', type=str, required=True, help="password cannot be blank!")


class Login(Resource):

    def post(self):
        args = parser_login.parse_args()
        username = args.get('username')
        password = args.get('password')
        user = User.query.filter(User.username == username).first()

        if not user:
            return jsonify({'status': 0, 'data': {}, 'msg': '用户不存在'})

        if not User.check_password(user, password):
            return jsonify({'status': 0, 'data': {}, 'msg': '用户密码错误,请重新输入'})

        # 触发session机制，通过user.get_id()就可以获取到token
        login_user(user)
        # 完成登录后将token存到缓存中并设置过期时间，后面校验时如果缓存中不存在，则报错
        life_time = current_app.config.get("TOKEN_LIFETIME")
        token = user.get_id(life_time)

        # 这样存数据,可以缓存多个token,  键值对 key 就是token,而不是value.
        simple_cache.set(token, 1, timeout=life_time)

        return jsonify({'status': 1, 'data': {'token': token, 'userdata': {
            'username': user.username, 'id': user.id, 'userstatus': user.status
        }}, 'msg': '登陆成功'})


class isLogin(Resource):
    @login_required
    def get(self):
        return jsonify({'status': 1, 'data': {}, 'msg': '已登录'})


class Logout(Resource):
    @login_required
    def get(self):
        logout_user()
        return jsonify({'status': 1, 'data': {}, 'msg': '退出成功'})


parser_pro = reqparse.RequestParser()
# 必需的参数:要求一个值传递的参数，只需要添加 required=True 来调用 add_argument()
parser_pro.add_argument('title', type=str, required=True, help="项目名不能为空!", )


class TestProject(Resource):
    @login_required
    def get(self):
        user_id = user_loader(session.get('user_id')).id
        project_lists = list(Project.query.filter(Project.author_id == user_id, Project.is_del == 0).all())

        project_list = []
        for project in project_lists:
            data_dict = {}
            data_dict['id'] = project.id
            data_dict['title'] = project.title
            project_list.append(data_dict)
        return jsonify({'status': 1, 'data': {'project_list': project_list}, 'message': 'Success'})

    @login_required
    def post(self):
        args = parser_pro.parse_args()
        title = args.get('title')
        author_id = user_loader(session.get('user_id')).id

        if Project.query.filter(Project.title == title, Project.is_del == 0).first():
            return jsonify({'status': 0, 'data': {}, 'message': '该项目名已被使用,请重新填写'})

        new_project = Project(title=title, author_id=author_id, env_id=1)
        db.session.add(new_project)
        db.session.commit()
        return jsonify({'status': 1, 'data': {}, 'message': '创建项目成功'})


class ProjectDetail(Resource):
    @login_required
    def put(self, project_id):
        args = parser_pro.parse_args()
        title = args.get('title')
        if Project.query.filter(Project.title == title, Project.is_del == 0).first():
            return jsonify({'status': '0', 'data': {}, 'message': '该项目名已被使用,请重新填写'})

        entity = Project.query.filter(Project.id == project_id).first()
        entity.title = title
        db.session.commit()
        return jsonify({'status': 1, 'data': project_id, 'message': 'Success'})

    @login_required
    def delete(self, project_id):
        entity = Project.query.filter(Project.id == project_id).first()
        entity.is_del = 1
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'message': '删除成功'})
