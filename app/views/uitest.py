from flask import jsonify
from ext import db
from flask_login import login_required
from flask_restful import Resource, reqparse
from app.models import Page, Element, Action, FunctionInfo
from sqlalchemy.exc import IntegrityError
parser_page = reqparse.RequestParser()
parser_page.add_argument('title', type=str, required=True, help="title cannot be blank!")


class PageList(Resource):
    @login_required
    def get(self, project_id):
        results = list(Page.query.filter(Page.project_id == project_id).all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"page_list": data_list}, 'msg': 'success'})

    @login_required
    def post(self, project_id):
        args = parser_page.parse_args()
        title = args.get('title')

        entity = Page(title=title, project_id=project_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'msg': 'success'})


class PageDetail(Resource):
    @login_required
    def put(self, project_id, page_id):
        args = parser_page.parse_args()
        title = args.get('title')
        entity = Page.query.filter(Page.id == page_id, Page.project_id == project_id).first()
        entity.title = title
        db.session.commit()
        return jsonify({'status': '1', 'data': {'title': title}, 'msg': 'success'})

    @login_required
    def delete(self, project_id, page_id):
        entity = Page.query.filter(Page.id == page_id, Page.project_id == project_id).first()
        db.session.delete(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'msg': 'success'})


parser_ele = reqparse.RequestParser()
parser_ele.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_ele.add_argument('type', type=str, help="type cannot be blank!")
parser_ele.add_argument('loc', type=str, help="loc cannot be blank!")
class ElementList(Resource):
    @login_required
    def get(self, project_id, page_id):
        results = list(Element.query.filter(Element.page_id == page_id).all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_dict['type'] = row.type
            data_dict['loc'] = row.loc
            data_dict['page_id'] = row.page_id
            data_dict['create_datetime'] = str(row.create_datetime)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'msg': 'success'})

    @login_required
    def post(self, project_id, page_id):
        args = parser_ele.parse_args()
        title = args.get('title')
        type = args.get('type')
        loc = args.get('loc')
        entity = Element(title=title, type=type, loc=loc, page_id=page_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'msg': 'success'})


parser_ele_detail = reqparse.RequestParser()
parser_ele_detail.add_argument('formData', type=str,action='append', help="formData cannot be blank!")
class ElementDetail(Resource):
    @login_required
    def put(self, project_id, page_id ,element_id):
        args = parser_ele.parse_args()
        entity = Element.query.filter(Element.id == element_id).first()
        entity.title = args.title
        entity.type = args.type
        entity.loc = args.loc
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'msg': 'success'})

    def delete(self, project_id, page_id, element_id):
        entity = Element.query.filter(Element.id == element_id).first()
        try:
            if entity:
                db.session.delete(entity)
                db.session.commit()
                return jsonify(
                    {'status': '1', 'data': element_id, 'msg': 'success'})
        except IntegrityError as e:

            return jsonify(
                {'status': '0', 'data': element_id, 'msg': "需要先删除或修改元素操作里面关联的元素信息"})



parser_act = reqparse.RequestParser()
parser_act.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_act.add_argument('functionId', type=str,required=True, help="function_id cannot be blank!")
parser_act.add_argument('elementId', type=str,required=True, help="element_id cannot be blank!")
class ActionList(Resource):
    @login_required
    def get(self, project_id, page_id):
        results = list(Action.query.filter(Action.page_id == page_id).all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_dict['fun_id'] = row.fun_id
            fun_title = FunctionInfo.query.filter(FunctionInfo.id == row.fun_id).first().title
            data_dict['fun_title'] = fun_title
            data_dict['ele_id'] = row.ele_id
            ele_title = Element.query.filter(Element.id == row.ele_id).first().title
            data_dict['ele_title'] = ele_title
            data_dict['page_id'] = row.page_id
            data_dict['create_datetime'] = str(row.create_datetime)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
            print(row.create_datetime)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'msg': 'success'})

    @login_required
    def post(self, project_id, page_id):
        args = parser_act.parse_args()
        title = args.get('title')
        function_id = args.get('functionId')
        element_id = args.get('elementId')

        entity = Action(title=title, fun_id=function_id, ele_id=element_id, page_id=page_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'msg': 'success'})



class ActionDetail(Resource):
    @login_required
    def put(self, project_id, page_id, action_id):
        args = parser_act.parse_args()
        print(args)
        entity = Action.query.filter(Action.id == action_id).first()
        entity.title = args.title
        entity.fun_id = args.functionId
        entity.ele_id = args.elementId
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'msg': 'success'})


    @login_required
    def delete(self, project_id, page_id, action_id):
        entity = Action.query.filter(Action.id == action_id ).first()
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': action_id, 'msg': 'success'})


parser_fun = reqparse.RequestParser()
parser_fun.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_fun.add_argument('type', type=int, required=True, help="type cannot be blank!")
parser_fun.add_argument('description', type=str, help="description cannot be blank!")
class FunctionList(Resource):
    @login_required
    def get(self):
        results = list(FunctionInfo.query.filter().all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_dict['type'] = row.type
            data_dict['description'] = row.description
            data_dict['create_datetime'] = str(row.create_datetime)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'msg': 'success'})

    @login_required
    def post(self):
        args = parser_fun.parse_args()
        title = args.get('title')
        type = args.get('type')
        description = args.get('description')

        entity = FunctionInfo(title=title, type=type, description=description)
        try:
            db.session.add(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': {}, 'msg': 'success'})
        except IntegrityError:
            return jsonify(
                {'status': '0', 'data': {}, 'msg': '名称重复'})



class FunctionDetail(Resource):
    @login_required
    def put(self,function_id):
        args = parser_fun.parse_args()
        print(args)
        entity = FunctionInfo.query.filter(FunctionInfo.id == function_id).first()
        entity.title = args.title
        entity.type = args.type
        entity.description = args.description
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'msg': 'success'})


    @login_required
    def delete(self, function_id):
        entity = FunctionInfo.query.filter(FunctionInfo.id == function_id ).first()
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': function_id, 'msg': 'success'})
