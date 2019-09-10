from flask import jsonify
from ext import db
from flask_login import login_required
from flask_restful import Resource, reqparse
from app.models import Page, Element, Action, FunctionInfo, TestCase, TestCaseSuit
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
parser_ele_detail.add_argument('formData', type=str, action='append', help="formData cannot be blank!")


class ElementDetail(Resource):
    @login_required
    def put(self, project_id, page_id, element_id):
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
parser_act.add_argument('functionId', type=str, required=True, help="function_id cannot be blank!")
parser_act.add_argument('elementId', type=str, required=True, help="element_id cannot be blank!")


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
        entity = Action.query.filter(Action.id == action_id).first()
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
    def put(self, function_id):
        args = parser_fun.parse_args()
        entity = FunctionInfo.query.filter(FunctionInfo.id == function_id).first()
        entity.title = args.title
        entity.type = args.type
        entity.description = args.description
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'msg': 'success'})

    @login_required
    def delete(self, function_id):
        entity = FunctionInfo.query.filter(FunctionInfo.id == function_id).first()
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': function_id, 'msg': 'success'})


parser_case = reqparse.RequestParser()
parser_case.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_case.add_argument('action_id', type=int, required=True, help="action_id cannot be blank!")


class TestCaseList(Resource):

    def case_list(self, project_id):
        results = list(TestCase.query.filter(TestCase.project_id == project_id).all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_dict['action_id'] = row.action_id
            action = Action.query.filter(Action.id == row.action_id).first()
            data_dict['action_title'] = action.title
            data_dict['create_datetime'] = str(row.create_datetime)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return data_list

    @login_required
    def get(self, project_id):
        data_list = self.case_list(project_id)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'msg': 'success'})
    @login_required
    def post(self, project_id):
        args = parser_case.parse_args()
        title = args.get('title')
        action_id = args.get('action_id')

        entity = TestCase(title=title, action_id=action_id, project_id=project_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'msg': 'success'})


class TestCaseDetail(Resource):
    @login_required
    def put(self, project_id, case_id):
        args = parser_case.parse_args()
        entity = TestCase.query.filter(TestCase.id == case_id).first()
        entity.title = args.title
        entity.action_id = args.action_id
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'msg': 'success'})

    @login_required
    def delete(self, project_id, case_id):
        entity = TestCase.query.filter(TestCase.id == case_id).first()
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': case_id, 'msg': 'success'})


parser_suit = reqparse.RequestParser()
parser_suit.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_suit.add_argument('test_case_ids', type=str, required=True, help="test_case_ids cannot be blank!")
parser_suit.add_argument('description', type=str, required=True, help="description cannot be blank!")
class CaseSuitList(Resource):
    def case_list_get(self, ids):
        results = list(TestCase.query.filter(TestCase.id.in_(ids)).all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_dict['action_id'] = row.action_id
            action = Action.query.filter(Action.id == row.action_id).first()
            data_dict['action_title'] = action.title
            data_dict['create_datetime'] = str(row.create_datetime)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return data_list

    # @login_required
    def get(self, project_id):
        results = list(TestCaseSuit.query.filter(TestCaseSuit.project_id == project_id).all())
        data_list = []
        for row in results:
            case_list = []
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_dict['test_case_ids'] = row.test_case_ids
            data_dict['description'] = row.description
            case_list = self.case_list_get(row.test_case_ids)
            data_dict['TestCaseList'] = case_list
            data_dict['create_datetime'] = str(row.create_datetime)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'msg': 'success'})

    @login_required
    def post(self, project_id):
        args = parser_suit.parse_args()
        print(args)
        title = args.get('title')
        description = args.get('description')
        test_case_ids = args.get('test_case_ids')
        print(test_case_ids)
        entity = TestCaseSuit(title=title, description=description, test_case_ids=test_case_ids, project_id=project_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'msg': 'success'})


class CaseSuitDetail(Resource):
    @login_required
    def put(self, project_id, case_suit_id):
        args = parser_suit.parse_args()
        entity = TestCaseSuit.query.filter(TestCaseSuit.id == case_suit_id).first()
        entity.title = args.title
        entity.description = args.description
        entity.test_case_ids = args.test_case_ids
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'msg': 'success'})

    @login_required
    def delete(self, project_id, case_suit_id):
        entity = TestCaseSuit.query.filter(TestCaseSuit.id == case_suit_id).first()
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': case_suit_id, 'msg': 'success'})
