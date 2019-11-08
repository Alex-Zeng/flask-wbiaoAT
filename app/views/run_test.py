from flask_login import login_required
from flask_restful import Resource, reqparse
import json
from base.driver_objects import td
from app.models import *
from collections import deque

parser_em = reqparse.RequestParser()
parser_em.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_em.add_argument('setting_args', type=str, required=True, help="title cannot be blank!")
parser_em.add_argument('remoteHost', type=str, required=True, help="title cannot be blank!")
parser_em.add_argument('remotePort', type=str, required=True, help="title cannot be blank!")


class EquipmentManagementList(Resource):
    @login_required
    def get(self):
        results = list(EquipmentManagement.query.all())
        return jsonify({'status': '1', 'data': {"data_list": model_to_dict(results)}, 'message': 'success'})

    @login_required
    def post(self):
        args = parser_em.parse_args()
        entity = EquipmentManagement(title=args.title, setting_args=args.setting_args,
                                     remoteHost=args.remoteHost, remotePort=args.remotePort)
        db.session.add(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'message': 'success'})


class EquipmentManagementDetail(Resource):
    @login_required
    def put(self, e_id):
        args = parser_em.parse_args()
        entity = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        entity.title = args.title
        entity.setting_args = args.setting_args
        entity.remoteHost = args.remoteHost
        entity.remotePort = args.remotePort
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': 'success'})

    @login_required
    def delete(self, e_id):
        entity = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        db.session.delete(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': e_id, 'message': 'success'})


# 启动appium session



class StartSession(Resource):
    @staticmethod
    def start(e_id):
        results = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        phone_info = model_to_dict(results)
        phone_info['setting_args'] = json.loads(phone_info['setting_args'])
        driver = td.start(phone_info)
        results.status = 1
        results.session_id = driver.session_id
        db.session.commit()
        return driver

    # @login_required
    def get(self, e_id):
        driver = self.start(e_id)
        return jsonify({'status': '1', 'data': driver.session_id, 'message': 'success'})


# 停止appium session
class StopSession(Resource):

    @staticmethod
    def stop(e_id):
        results = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        if results.session_id:
            msg = td.quit(results.session_id)
            results.status = 0
            results.session_id = ''
            db.session.commit()
            return msg
        else:
            return '退出失败'

    # @login_required
    def get(self, e_id):
        msg = self.stop(e_id)
        return jsonify({'status': '1', 'data': '', 'message': msg})


parser_sc = reqparse.RequestParser()
parser_sc.add_argument('e_id', type=int, required=True, help="e_id cannot be blank!")
parser_sc.add_argument('input_args', type=str, help="input_args")
# 调试单个用例
class StartCase(Resource):
    # 解析用例
    def analysis_case(self, case_entity, case_args):
        case_list = []
        items = case_entity.step
        case_id = case_entity.id
        case_title = case_entity.title
        case_args_dict={}
        try:
            if case_args:
                case_args_dict = json.loads(case_args)
        except Exception:
            return '参数非法: 不符合json格式,请仔细检查参数'

        if case_args_dict:
            for k,v in case_args_dict.items():
                if isinstance(v,list):
                    case_args_dict[k] = deque(v)
                else:
                    return '参数非法: 值不是列表形式'

        for item in items:
            case_dict = {}
            case_dict['case_id'] = '{}-{}'.format(case_id, item.rank)
            case_dict['case_title'] = case_title
            case_dict['action'] = item.action.fun.fun_title
            case_dict['action_title'] = item.action.title
            case_dict['element_loc'] = item.action.ele.loc
            case_dict['element_info'] = item.action.ele.title
            case_dict['type'] = item.action.ele.type
            case_dict['screen_shot'] = item.take_screen_shot
            case_dict['wait_time'] = item.wait_time
            case_dict['output_arg'] = item.output_key
            if item.input_key:
                try:
                    case_dict['input_arg'] = case_args_dict.get(item.input_key).popleft()
                except:
                    pass
                    # return '未找到对应参数'
            else:
                case_dict['input_arg'] = ''
            case_list.append(case_dict)
        return case_list


    # @login_required
    def post(self,project_id, case_id):
        args = parser_sc.parse_args()
        # StartSession.start(args.e_id)
        case_entity = TestCase.query.filter(TestCase.id == case_id).first()
        # print(args.input_args)
        case_list = self.analysis_case(case_entity,args.input_args)
        print(case_list)


# 调试用例集
class StartCasSuit(Resource):
    # @login_required
    def get(self, e_id):
        entity = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        print(entity)
