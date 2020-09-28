import json

from flask_restful import Resource, reqparse
from app.models import *
from sqlalchemy.exc import IntegrityError

parser_page = reqparse.RequestParser()
parser_page.add_argument('title', type=str, nullable=False, help="title cannot be blank!")
parser_page.add_argument('parentId', type=int, help="parentId cannot be blank!")


# 页面
class PageList(Resource):
    def list_data(self, id, results, p_title=''):
        data_list = []
        for row in results:
            if row.parent_directory == id:
                data_dict = {}
                data_dict['id'] = row.id
                data_dict['value'] = row.id
                data_dict['label'] = row.title
                data_dict['title'] = row.title
                data_dict['parent_directory'] = row.parent_directory
                data_dict['parent_title'] = p_title
                children = self.list_data(row.id, results, row.title)
                if children:
                    data_dict['children'] = children
                data_list.append(data_dict)
        return data_list

    # @login_required
    def get(self, project_id):
        results = list(Page.query.filter(Page.project_id == project_id, Page.is_del == 0).all())
        if not results:
            return jsonify({'status': 0, 'data': [], 'message': 'Empty'})
        data_list = self.list_data(0, results)
        return jsonify({'status': '1', 'data': {"page_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id):
        args = parser_page.parse_args()
        title = args.get('title')
        p_id = args.parentId if args.parentId else 0
        entity = Page(title=title, project_id=project_id, parent_directory=p_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'message': 'success'})


# 页面内容
class PageDetail(Resource):
    # @login_required
    def put(self, project_id, page_id):
        args = parser_page.parse_args()
        entity = Page.query.filter(Page.id == page_id, Page.project_id == project_id).first()
        if args.title:
            entity.title = args.title
        entity.parent_directory = args.parentId
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': '修改页面成功'})

    # @login_required
    def delete(self, project_id, page_id):
        entity = Page.query.filter(Page.id == page_id, Page.project_id == project_id).first()
        message = ''
        if entity.action:
            for act in entity.action:
                if act.step:
                    for st in act.step:
                        message += st.test_case.title + ','
                    return jsonify(
                        {'status': '0', 'data': {}, 'message': '用例{}有使用到该页面,请先解除关联'.format(message)})
                else:
                    db.session.delete(act)

        if entity.element:
            for ele in entity.element:
                db.session.delete(ele)
        db.session.delete(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'message': '删除页面成功'})


class pageCopy(Resource):

    def get(self, project_id, page_id):
        entity = Page.query.filter(Page.id == page_id, Page.project_id == project_id).first()
        entity_cp = Page(title='{}_副本'.format(entity.title), project_id=entity.project_id, parent_directory=entity.parent_directory)
        db.session.add(entity_cp)
        db.session.commit()

        for item in entity.element:
            entity_e = Element(title=item.title, type_for_ios=item.type_for_ios, loc_for_ios=item.loc_for_ios,
                             type_for_android=item.type_for_android, loc_for_android=item.loc_for_android,
                             page_id=entity_cp.id)
            db.session.add(entity_e)
        db.session.commit()

        for item in entity.action:

            new_page = Page.query.filter(Page.id == entity_cp.id).first()
            for ele in new_page.element:
                if ele.title == item.ele.title:
                    entity_a = Action(fun_id=item.fun_id, ele_id=ele.id, page_id=entity_cp.id)
                    db.session.add(entity_a)
        db.session.commit()
        return jsonify({'status': '1', 'data': {"data_list": ''}, 'message': '复制页面成功'})


parser_ele = reqparse.RequestParser()
parser_ele.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_ele.add_argument('type_for_android', type=str, help="type cannot be blank!")
parser_ele.add_argument('loc_for_android', type=str, help="loc cannot be blank!")
parser_ele.add_argument('loc_for_ios', type=str, help="loc cannot be blank!")
parser_ele.add_argument('type_for_ios', type=str, help="page_id wrong")
parser_ele.add_argument('page_id', type=int, help="page_id wrong")


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
            data_dict['type_for_android'] = row.type_for_android
            data_dict['loc_for_android'] = row.loc_for_android
            data_dict['type_for_ios'] = row.type_for_ios
            data_dict['loc_for_ios'] = row.loc_for_ios
            data_dict['page_id'] = row.page_id
            data_dict['page_title'] = row.page.title
            data_dict['create_datetime'] = str(row.create_datetime)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id, page_id):
        args = parser_ele.parse_args()
        title = args.title
        type_for_android = args.type_for_android
        loc_for_android = args.loc_for_android.strip()
        type_for_ios = args.type_for_ios
        loc_for_ios = args.loc_for_ios.strip()
        entity = Element(title=title, type_for_ios=type_for_ios, loc_for_ios=loc_for_ios,
                         type_for_android=type_for_android, loc_for_android=loc_for_android, page_id=page_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'message': 'success'})


# 元素内容
class ElementDetail(Resource):
    # @login_required
    def put(self, project_id, page_id, element_id):
        args = parser_ele.parse_args()
        entity = Element.query.filter(Element.id == element_id).first()
        entity.title = args.title
        entity.type_for_android = args.type_for_android
        if args.loc_for_android:
            entity.loc_for_android = args.loc_for_android.strip()
        entity.type_for_ios = args.type_for_ios
        if args.loc_for_ios:
            entity.loc_for_ios = args.loc_for_ios.strip()
        entity.page_id = args.page_id
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': 'success'})

    # @login_required
    def delete(self, project_id, page_id, element_id):
        entity = Element.query.filter(Element.id == element_id).first()
        act = Action.query.filter(Action.ele_id == element_id).all()
        if len(act) > 0:
            act_list = ''
            for a in act:
                act_list += '页面:{}下id为{}的操作,'.format(a.page.title, a.id)
            return jsonify(
                {'status': 0, 'data': element_id, 'message': "需要先删除或修改元素操作--{} 里面关联的元素信息".format(act_list)})
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': 1, 'data': element_id, 'message': 'success'})


parser_act = reqparse.RequestParser()
parser_act.add_argument('fun_id', type=str, required=True, help="fun_id cannot be blank!")
parser_act.add_argument('ele_id', type=str, required=True, help="ele_id cannot be blank!")
parser_act.add_argument('page_id', type=int, help="page_id")


# 操作
class ActionList(Resource):
    # @login_required
    def get(self, project_id, page_id):
        results = list(Action.query.filter(Action.page_id == page_id).all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = '在[{}]页面-[{}]-[{}]元素'.format(row.page.title, row.fun.title, row.ele.title)
            data_dict['fun_id'] = row.fun_id
            data_dict['fun_title'] = row.fun.title
            data_dict['ele_id'] = row.ele_id
            data_dict['ele_title'] = row.ele.title
            data_dict['page_id'] = row.page_id
            data_dict['page_title'] = row.page.title
            data_dict['create_datetime'] = str(row.create_datetime)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': 1, 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id, page_id):
        args = parser_act.parse_args()
        entity = Action(fun_id=args.fun_id, ele_id=args.ele_id, page_id=page_id)
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
        entity.fun_id = args.fun_id
        entity.ele_id = args.ele_id
        entity.page_id = args.page_id
        db.session.commit()
        return jsonify({'status': 1, 'data': args, 'message': 'success'})

    # @login_required
    def delete(self, project_id, page_id, action_id):
        entity = Action.query.filter(Action.id == action_id).first()
        if entity.step:
            message = ''
            for item in entity.step:
                message += '[标题:{}--步骤:{}]---,'.format(item.test_case.title, item.title)
            return jsonify(
                {'status': 0, 'data': action_id, 'message': '该操作已关联用例-----{}-----请先删除或修改相关用例'.format(message)})
        elif entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': 1, 'data': action_id, 'message': '操作{}删除'.format(entity.id)})


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
parser_case.add_argument('title', type=str, trim=True, help="title cannot be blank!")
parser_case.add_argument('parentId', type=int, help="title cannot be blank!")


# 用例
class TestCaseList(Resource):
    def list_data(self, id, results, p_title=''):
        data_list = []
        for row in results:
            if row.parent_directory == id:
                data_dict = {}
                data_dict['id'] = row.id
                data_dict['value'] = row.id
                data_dict['label'] = row.title
                data_dict['title'] = row.title
                data_dict['parent_directory'] = row.parent_directory
                data_dict['parent_title'] = p_title
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
                children = self.list_data(row.id, results, row.title)
                if children:
                    data_dict['children'] = children
                data_list.append(data_dict)
        return data_list

    # @login_required
    def get(self, project_id):
        results = list(
            TestCase.query.filter(TestCase.project_id == project_id, TestCase.is_del == 0).order_by(
                db.desc(TestCase.update_datetime)).all())
        data_list = self.list_data(0, results)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id):
        args = parser_case.parse_args()
        title = args.get('title')
        if not title:
            return jsonify({'status': '0', 'data': {}, 'message': 'title不能为空'})
        p_id = args.parentId if args.parentId else 0
        entity = TestCase(title=title, project_id=project_id, parent_directory=p_id, is_del=0, )
        db.session.add(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'message': 'success'})


# 用例内容
class TestCaseDetail(Resource):
    # @login_required
    def put(self, project_id, case_id):
        args = parser_case.parse_args()
        entity = TestCase.query.filter(TestCase.id == case_id).first()
        if args.title:
            entity.title = args.title
        entity.parent_directory = args.parentId
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': '修改用例内容成功'})

    # @login_required
    def delete(self, project_id, case_id):
        entity = TestCase.query.filter(TestCase.id == case_id).first()
        if entity.suit:
            suit_titles = ''
            for item in entity.suit:
                suit_titles += '<<{}>>,'.format(item.title)
            return jsonify(
                {'status': '0', 'data': case_id, 'message': '请先删除该用例关联的用例集{}'.format(suit_titles)})
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': case_id, 'message': 'success'})


class TestCaseCopy(Resource):

    def get(self, project_id, case_id):
        entity = TestCase.query.filter(TestCase.id == case_id).first()
        entity_cp = TestCase(title='{}_副本'.format(entity.title), project_id=entity.project_id,
                             parent_directory=entity.parent_directory, is_del=0)
        db.session.add(entity_cp)
        db.session.commit()
        for item in entity.step:
            entity = TestCaseStep(rank=item.rank, title=item.title, action_id=item.action_id, skip=item.skip,
                                  take_screen_shot=item.take_screen_shot, wait_time=item.wait_time,
                                  test_case_id=entity_cp.id,
                                  input_key=item.input_key,
                                  output_key=item.output_key)
            db.session.add(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {"data_list": ''}, 'message': '复制用例成功'})


parser_step = reqparse.RequestParser()
parser_step.add_argument('rank', type=int, required=True, help="rank cannot be blank and must be number!")
parser_step.add_argument('skip', type=int, required=True, help="skip cannot be blank and must be number!")
parser_step.add_argument('action_id', type=str, required=True, help="action_id cannot be blank!")
parser_step.add_argument('output_key', type=str, help="output_key error")
parser_step.add_argument('title', type=str, help="title error")
parser_step.add_argument('input_key', type=str, help="input_key error!")
parser_step.add_argument('wait_time', type=int, help="wait_time error!")
parser_step.add_argument('take_screen_shot', type=int, help="take_screen_shot error!")


# 用例步骤
class TestCaseStepList(Resource):

    def rank_repeat_than_plus(self, rank, case_id):
        # 检查是否是有重复的步骤,如果有加1

        entity = TestCaseStep.query.filter(TestCaseStep.rank == rank, TestCaseStep.test_case_id == case_id).first()
        if entity:
            new_rank = self.rank_repeat_than_plus(rank + 1, case_id)
            return new_rank
        else:
            return rank

    # @login_required
    def get(self, project_id, case_id):
        result = TestCase.query.filter(TestCase.id == case_id).first()
        data_list = []
        if not result:
            return jsonify({'status': 1, 'data': "", 'message': 'Empty'})
        for row in result.step:
            data_dict = {}
            data_dict['id'] = row.id

            data_dict['rank'] = row.rank
            data_dict['title'] = row.title
            data_dict['input_key'] = row.input_key
            data_dict['output_key'] = row.output_key
            data_dict['action_id'] = row.action.id
            data_dict['skip'] = row.skip
            data_dict['take_screen_shot'] = row.take_screen_shot
            data_dict['wait_time'] = row.wait_time
            data_dict['page_id'] = row.action.page.id
            data_dict['ele_id'] = row.action.ele.id
            data_dict['page_title'] = row.action.page.title
            data_dict['action_title'] = '在[{}页面]-[{}]-[{}元素]'.format(row.action.page.title, row.action.fun.title,
                                                                     row.action.ele.title)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id, case_id):
        args = parser_step.parse_args()
        final_rank = self.rank_repeat_than_plus(args.rank, case_id)
        entity = TestCaseStep(rank=final_rank, title=args.title, skip=0, action_id=args.action_id,
                              input_key=args.input_key,
                              output_key=args.output_key, take_screen_shot=args.take_screen_shot,
                              wait_time=args.wait_time, test_case_id=case_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': {}, 'message': 'success'})


# 用例步骤内容
class TestCaseStepDetail(Resource):
    def update_rank(self, case_id, rank, step_id):
        up_rank = rank
        up_step_id = step_id
        # 同一条用例下,不同步骤,相同排序
        result = TestCaseStep.query.filter(TestCaseStep.test_case_id == case_id, TestCaseStep.rank == rank,
                                           TestCaseStep.id != step_id).first()
        if result:
            result.rank = rank + 1
            up_rank = result.rank
            up_step_id = result.id
            db.session.flush()
        else:
            db.session.commit()
            return

        self.update_rank(case_id, up_rank, up_step_id)

    def init_rank(self, case_id):
        # 重新排序
        result = TestCase.query.filter(TestCase.id == case_id).first()
        # results = TestCaseStep.query.filter(TestCaseStep.test_case_id == case_id).all()
        init_rank = 1
        for item in result.step:
            result = TestCaseStep.query.filter(TestCaseStep.id == item.id).first()
            result.rank = init_rank
            init_rank += 1
            db.session.flush()
        db.session.commit()

    # @login_required
    def put(self, project_id, case_id, step_id):
        args = parser_step.parse_args()
        self.update_rank(case_id, args.rank, step_id)
        entity = TestCaseStep.query.filter(TestCaseStep.id == step_id).first()
        entity.action_id = args.action_id
        entity.title = args.title
        entity.wait_time = args.wait_time
        entity.take_screen_shot = args.take_screen_shot
        entity.input_key = args.input_key
        entity.output_key = args.output_key
        entity.skip = args.skip
        entity.rank = args.rank
        db.session.flush()
        db.session.commit()
        # self.init_rank(case_id)
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
parser_suit.add_argument('title', type=str, nullable=False, help="title cannot be blank!")
parser_suit.add_argument('parentId', type=int, help="parentId cannot be blank!")


# 用例集
class CaseSuitList(Resource):
    def list_data(self, id, results, p_title=''):
        data_list = []
        for row in results:
            if row.parent_directory == id:
                data_dict = {}
                data_dict['id'] = row.id
                data_dict['value'] = row.id
                data_dict['label'] = row.title
                data_dict['title'] = row.title
                data_dict['parent_directory'] = row.parent_directory
                data_dict['parent_title'] = p_title
                children = self.list_data(row.id, results, row.title)
                if children:
                    data_dict['children'] = children
                data_list.append(data_dict)
        return data_list

    # # @login_required
    def get(self, project_id):
        results = list(TestCaseSuit.query.filter(TestCaseSuit.project_id == project_id, TestCaseSuit.is_del == 0).all())
        if not results:
            return jsonify({'status': 0, 'data': [], 'message': 'Empty'})
        data_list = self.list_data(0, results)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, project_id):
        args = parser_suit.parse_args()
        p_id = args.parentId if args.parentId else 0
        entity = TestCaseSuit(title=args.title, project_id=project_id, parent_directory=p_id)
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
        if args.title:
            entity.title = args.title
        entity.parent_directory = args.parentId
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': '修改用例集成功'})

    # @login_required
    def delete(self, project_id, suit_id):
        entity = TestCaseSuit.query.filter(TestCaseSuit.id == suit_id).first()
        if entity:
            entity.is_del = 1
            db.session.commit()
            return jsonify(
                {'status': '1', 'data': suit_id, 'message': 'success'})


class CaseSuitCopy(Resource):
    """
    用例集复制
    """

    # @login_required
    def get(self, project_id, suit_id):
        entity = TestCaseSuit.query.filter(TestCaseSuit.id == suit_id).first()
        entity_cp = TestCaseSuit(title='{}_副本'.format(entity.title), project_id=entity.project_id,
                                 parent_directory=entity.parent_directory)
        db.session.add(entity_cp)
        for item in entity.suit_step:
            entity = TestSuitStep(rank=item.rank, skip=item.skip, test_case_id=item.test_case_id,
                                  test_case_suit_id=entity_cp.id,
                                  input_args=item.input_args)
            db.session.add(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {"data_list": ''}, 'message': '复制成功'})


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
    def update_rank(self, suit_id, rank, step_id):
        up_rank = rank
        up_step_id = step_id
        # 同一条用例下,不同步骤,相同排序
        result = TestSuitStep.query.filter(TestSuitStep.test_case_suit_id == suit_id, TestSuitStep.rank == rank,
                                           TestSuitStep.id != step_id).first()
        if result:
            result.rank = rank + 1
            up_rank = result.rank
            up_step_id = result.id
            db.session.commit()
        else:
            return

        self.update_rank(suit_id, up_rank, up_step_id)

    # @login_required
    def put(self, project_id, suit_id, step_id):
        args = parser_suit_step.parse_args()
        self.update_rank(suit_id, args.rank, step_id)
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
