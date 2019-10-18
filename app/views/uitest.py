import json

from flask import jsonify
from ext import db
from flask_login import login_required
from flask_restful import Resource, reqparse
from app.models import *
from sqlalchemy.exc import IntegrityError

parser_page = reqparse.RequestParser()
parser_page.add_argument('title', type=str, required=True, help="title cannot be blank!")


# 页面
class PageList(Resource):
    # @login_required
    def get(self, project_id):
        results = list(Page.query.filter(Page.project_id == project_id).all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"page_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id):
        args = parser_page.parse_args()
        title = args.get('title')

        entity = Page(title=title, project_id=project_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'message': 'success'})


# 页面内容
class PageDetail(Resource):
    # @login_required
    def put(self, project_id, page_id):
        args = parser_page.parse_args()
        title = args.get('title')
        entity = Page.query.filter(Page.id == page_id, Page.project_id == project_id).first()
        entity.title = title
        db.session.commit()
        return jsonify({'status': '1', 'data': {'title': title}, 'message': 'success'})

    # @login_required
    def delete(self, project_id, page_id):
        entity = Page.query.filter(Page.id == page_id, Page.project_id == project_id).first()
        message = ''
        if entity.action:
            for act in entity.action:
                print(act.title)
                if act.step:
                    for st in act.step:
                        message += st.test_case.title + ','
        if message:
            return jsonify({'status': '0', 'data': {}, 'message': '用例{}有使用到该页面,请先修改或删除用例{}'.format(message, message)})
        db.session.delete(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'message': 'success'})


parser_ele = reqparse.RequestParser()
parser_ele.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_ele.add_argument('type', type=str, help="type cannot be blank!")
parser_ele.add_argument('loc', type=str, help="loc cannot be blank!")


# 元素
class ElementList(Resource):
    # @login_required
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
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id, page_id):
        args = parser_ele.parse_args()
        title = args.get('title')
        type = args.get('type')
        loc = args.get('loc')
        entity = Element(title=title, type=type, loc=loc, page_id=page_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'message': 'success'})


parser_ele_detail = reqparse.RequestParser()
parser_ele_detail.add_argument('formData', type=str, action='append', help="formData cannot be blank!")


# 元素内容
class ElementDetail(Resource):
    # @login_required
    def put(self, project_id, page_id, element_id):
        args = parser_ele.parse_args()
        entity = Element.query.filter(Element.id == element_id).first()
        entity.title = args.title
        entity.type = args.type
        entity.loc = args.loc
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': 'success'})

    # @login_required
    def delete(self, project_id, page_id, element_id):
        entity = Element.query.filter(Element.id == element_id).first()
        act = Action.query.filter(Action.ele_id == element_id).all()
        if len(act) > 0:
            act_list = ''
            for a in act:
                act_list += str(a.id) + ','
            return jsonify(
                {'status': '0', 'data': element_id, 'message': "需要先删除或修改元素操作ID为: {} 里面关联的元素信息".format(act_list)})
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': element_id, 'message': 'success'})


parser_act = reqparse.RequestParser()
parser_act.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_act.add_argument('fun_id', type=str, required=True, help="fun_id cannot be blank!")
parser_act.add_argument('ele_id', type=str, required=True, help="ele_id cannot be blank!")


# 操作
class ActionList(Resource):
    # @login_required
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
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id, page_id):
        args = parser_act.parse_args()
        entity = Action(title=args.title, fun_id=args.fun_id, ele_id=args.ele_id, page_id=page_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'message': 'success'})


# 操作内容
class ActionDetail(Resource):
    # @login_required
    def put(self, project_id, page_id, action_id):
        args = parser_act.parse_args()
        print(args)
        entity = Action.query.filter(Action.id == action_id).first()
        entity.title = args.title
        entity.fun_id = args.fun_id
        entity.ele_id = args.ele_id
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': 'success'})

    # @login_required
    def delete(self, project_id, page_id, action_id):
        entity = Action.query.filter(Action.id == action_id).first()
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': action_id, 'message': 'success'})


parser_fun = reqparse.RequestParser()
parser_fun.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_fun.add_argument('fun_title', type=str, required=True, help="fun_title cannot be blank!")
parser_fun.add_argument('type', type=int, required=True, help="type cannot be blank!")
parser_fun.add_argument('description', type=str, help="description cannot be blank!")


# 操作方法
class FunctionList(Resource):

    # @login_required
    def get(self):
        results = list(FunctionInfo.query.filter().all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_dict['fun_title'] = row.fun_title
            data_dict['type'] = row.type
            data_dict['description'] = row.description
            data_dict['create_datetime'] = str(row.create_datetime)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self):
        args = parser_fun.parse_args()
        entity = FunctionInfo(title=args.title, type=args.type, fun_title=args.fun_title, description=args.description)
        try:
            db.session.add(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': {}, 'message': 'success'})
        except IntegrityError:
            return jsonify(
                {'status': '0', 'data': {}, 'message': '名称重复'})


# 操作方法内容
class FunctionDetail(Resource):
    # @login_required
    def put(self, function_id):
        args = parser_fun.parse_args()
        entity = FunctionInfo.query.filter(FunctionInfo.id == function_id).first()
        entity.title = args.title
        entity.fun_title = args.fun_title
        entity.type = args.type
        entity.description = args.description
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': 'success'})

    # @login_required
    def delete(self, function_id):
        entity = FunctionInfo.query.filter(FunctionInfo.id == function_id).first()
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': function_id, 'message': 'success'})


parser_case = reqparse.RequestParser()
parser_case.add_argument('title', type=str, required=True, help="title cannot be blank!")


# 用例
class TestCaseList(Resource):

    # @login_required
    def get(self, project_id):
        results = list(TestCase.query.filter(TestCase.project_id == project_id).all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            input_list = []
            out_list = []
            for step in row.step:
                if step.input_key:
                    input_list.append(step.input_key)
                if step.output_key:
                    out_list.append(step.output_key)

            data_dict['input_keys'] = ','.join(input_list)
            data_dict['output_keys'] = ','.join(out_list)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id):
        args = parser_case.parse_args()
        title = args.get('title')
        entity = TestCase(title=title, project_id=project_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'message': 'success'})


# 用例内容
class TestCaseDetail(Resource):
    # @login_required
    def put(self, project_id, case_id):
        args = parser_case.parse_args()
        entity = TestCase.query.filter(TestCase.id == case_id).first()
        entity.title = args.title
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': 'success'})

    # @login_required
    def delete(self, project_id, case_id):
        entity = TestCase.query.filter(TestCase.id == case_id).first()
        if entity.suit:
            return jsonify(
                {'status': '0', 'data': case_id, 'message': '请先删除用例集下面的关联此用例的步骤'})
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': case_id, 'message': 'success'})


parser_step = reqparse.RequestParser()
parser_step.add_argument('rank', type=int, required=True, help="rank cannot be blank and must be number!")
parser_step.add_argument('skip', type=int, required=True, help="skip cannot be blank and must be number!")
parser_step.add_argument('action_id', type=str, required=True, help="action_id cannot be blank!")
parser_step.add_argument('output_key', type=str, help="output_key error")
parser_step.add_argument('input_key', type=str, help="input_key error!")


# 用例步骤
class TestCaseStepList(Resource):
    # @login_required
    def get(self, project_id, case_id):
        results = list(TestCaseStep.query.filter(TestCaseStep.test_case_id == case_id).order_by(
            TestCaseStep.rank).all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['rank'] = row.rank
            data_dict['input_key'] = row.input_key
            data_dict['output_key'] = row.output_key
            data_dict['action_id'] = row.action.id
            data_dict['skip'] = row.skip
            data_dict['page_id'] = row.action.page.id
            data_dict['page_title'] = row.action.page.title
            data_dict['action_title'] = row.action.title
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id, case_id):
        args = parser_step.parse_args()
        has_entity = TestCaseStep.query.filter(TestCaseStep.rank == args.rank,
                                               TestCaseStep.test_case_id == case_id).first()
        if has_entity:
            return jsonify(
                {'status': '0', 'data': {}, 'message': '已存在步骤{}'.format(args.rank)})
        entity = TestCaseStep(rank=args.rank, skip=0, action_id=args.action_id, input_key=args.input_key,
                              output_key=args.output_key, test_case_id=case_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'message': 'success'})


# 用例步骤内容
class TestCaseStepDetail(Resource):
    # @login_required
    def put(self, project_id, case_id, step_id):
        args = parser_step.parse_args()
        entity = TestCaseStep.query.filter(TestCaseStep.id == step_id).first()
        entity.rank = args.rank
        entity.action_id = args.action_id
        entity.input_key = args.input_key
        entity.output_key = args.output_key
        entity.skip = args.skip
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': 'success'})

    # @login_required
    def delete(self, project_id, case_id, step_id):
        entity = TestCaseStep.query.filter(TestCaseStep.id == step_id).first()
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': step_id, 'message': 'success'})


parser_suit = reqparse.RequestParser()
parser_suit.add_argument('title', type=str, required=True, help="title cannot be blank!")


# 用例集
class CaseSuitList(Resource):

    # # @login_required
    def get(self, project_id):
        results = list(TestCaseSuit.query.filter(TestCaseSuit.project_id == project_id).all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_dict['create_datetime'] = str(row.create_datetime)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id):
        args = parser_suit.parse_args()
        entity = TestCaseSuit(title=args.title, project_id=project_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'message': 'success'})


# 用例集内容
class CaseSuitDetail(Resource):
    # @login_required
    def put(self, project_id, suit_id):
        args = parser_suit.parse_args()
        entity = TestCaseSuit.query.filter(TestCaseSuit.id == suit_id).first()
        entity.title = args.title
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': 'success'})

    # @login_required
    def delete(self, project_id, suit_id):
        entity = TestCaseSuit.query.filter(TestCaseSuit.id == suit_id).first()
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': suit_id, 'message': 'success'})


parser_suit_step = reqparse.RequestParser()
parser_suit_step.add_argument('rank', type=int, required=True, help="rank cannot be blank and must be number!")
parser_suit_step.add_argument('case_id', type=str, required=True, help="case_id cannot be blank!")
parser_suit_step.add_argument('input_args', type=str)
parser_suit_step.add_argument('skip', type=int)


# 用例集步骤
class TestSuitStepList(Resource):
    # @login_required
    def get(self, project_id, suit_id):
        results = list(TestSuitStep.query.filter(TestSuitStep.test_case_suit_id == suit_id).order_by(
            TestSuitStep.rank).all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['rank'] = row.rank
            data_dict['case_id'] = row.test_case_id
            data_dict['case_title'] = row.test_case.title
            data_dict['input_args'] = row.input_args
            data_dict['skip'] = row.skip
            input_list = []
            out_list = []
            for step in row.test_case.step:
                if step.input_key:
                    input_list.append(step.input_key)
                if step.output_key:
                    out_list.append(step.output_key)

            data_dict['case_title'] = row.test_case.title
            data_dict['input_keys'] = input_list
            data_dict['output_keys'] = out_list
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id, suit_id):
        args = parser_suit_step.parse_args()
        if args.input_args:
            input_a = json.dumps(json.loads(args.input_args))
        else:
            input_a = None

        has_entity = TestSuitStep.query.filter(TestSuitStep.rank == args.rank,
                                               TestSuitStep.test_case_suit_id == suit_id).first()
        if has_entity:
            return jsonify(
                {'status': '0', 'data': {}, 'message': '已存在步骤{}'.format(args.rank)})
        entity = TestSuitStep(rank=args.rank, skip=0, test_case_id=args.case_id, test_case_suit_id=suit_id,
                              input_args=input_a)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'message': 'success'})


# 用例集步骤内容
class TestSuitStepDetail(Resource):
    # @login_required
    def put(self, project_id, suit_id, step_id):
        args = parser_suit_step.parse_args()
        entity = TestSuitStep.query.filter(TestSuitStep.id == step_id).first()
        entity.rank = args.rank
        entity.test_case_id = args.case_id
        entity.skip = args.skip
        try:
            entity.input_args = json.dumps(json.loads(args.input_args))
        except:
            entity.input_args = args.input_args
        db.session.commit()
        return jsonify({'status': '1', 'data': entity.input_args, 'message': 'success'})

    # @login_required
    def delete(self, project_id, suit_id, step_id):
        entity = TestSuitStep.query.filter(TestSuitStep.id == step_id).first()
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': step_id, 'message': 'success'})
