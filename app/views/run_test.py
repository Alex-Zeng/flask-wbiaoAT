from flask_login import login_required
from flask_restful import Resource, reqparse
import time
from base.public.log import log_main
from base.driver_objects import td
from base.base_action import BaseAction
from base.public.utils import *
from app.models import *
from base.public.log import Log
import traceback
from multiprocessing import Process

parser_em = reqparse.RequestParser()
parser_em.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_em.add_argument('setting_args', type=str, required=True, help="title cannot be blank!")
parser_em.add_argument('remoteHost', type=str, required=True, help="remoteHost cannot be blank!")
parser_em.add_argument('remotePort', type=str, required=True, help="remotePort cannot be blank!")
class EquipmentManagementList(Resource):
    ''' 设备管理列表'''
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
    ''' 设备信息'''
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


parser_es = reqparse.RequestParser()
parser_es.add_argument('suit_id', type=int, required=True, help="test_case_suit_id cannot be blank!")
parser_es.add_argument('rank', type=int, required=True, help="rank cannot be blank!")
class EquipmentIncludeTestCaseSuitList(Resource):
    ''' 设备用例集列表'''
    # @login_required
    def get(self,e_id):
        results = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        data_list = []
        for row in results.test_case_suit:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['rank'] = row.rank
            data_dict['suit_title'] = model_to_dict(row.test_case_suit).get('title','')
            data_dict['suit_id'] = model_to_dict(row.test_case_suit).get('id','')
            test_cases_list = []
            for item in row.test_case_suit.suit_step:
                test_cases_list.append(item.test_case)
            data_dict['test_cases'] = model_to_dict(test_cases_list)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self,e_id):
        args = parser_es.parse_args()
        entity = EquipmentIncludeTesSuit(test_case_suit_id=args.suit_id, rank=args.rank, equipment_id=e_id)
        db.session.add(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'message': 'success'})

class EquipmentIncludeTestCaseSuitDetail(Resource):
    ''' 设备用例集信息'''
    # @login_required
    def put(self, e_id, es_id):
        args = parser_es.parse_args()

        entity = EquipmentIncludeTesSuit.query.filter(EquipmentIncludeTesSuit.id == es_id).first()
        entity.equipment_id = e_id
        entity.test_case_suit_id = args.suit_id
        entity.rank = args.rank
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': 'success'})

    # @login_required
    def delete(self,e_id, es_id):
        entity = EquipmentIncludeTesSuit.query.filter(EquipmentIncludeTesSuit.id == es_id).first()
        db.session.delete(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': es_id, 'message': 'success'})

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

    # 单条用例调试
    # @login_required
    def post(self,project_id, case_id):
        args = parser_sc.parse_args()
        case_entity = TestCase.query.filter(TestCase.id == case_id).first()
        log_run = Log('single_case_run')
        case_list = analysis_case(case_entity,args.input_args)
        driver = StartSession.start(args.e_id)
        ba = BaseAction(driver,case_entity.title,log_run)
        ba.action(case_list)


# 调试用例集
class StartCasSuit(Resource):

    def run_test_task(self,e_id):
        start = time.time()
        log_main.info('正在运行的任务：{}'.format(e_id))

        entity = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        et_title = entity.title
        log_run = Log('Equipment-{}'.format(e_id))
        driver = StartSession.start(e_id)
        for item in entity.test_case_suit:
            shot_title = '{}-{}'.format(et_title,item.test_case_suit.title)
            log_run.info('---------------------- 用例集开始: {} ----------------------'.format(shot_title))
            for step in item.test_case_suit.suit_step:
                if step.skip == 1:
                    continue
                log_run.info('用例{}-{},输入参数列表: {}'.format(step.test_case.id,step.test_case.title,step.input_args))
                case_entity = TestCase.query.filter(TestCase.id == step.test_case.id).first()
                case_list = analysis_case(case_entity,step.input_args)
                ba = BaseAction(driver, shot_title,log_run)
                ba.action(case_list)

            log_run.info('---------------------- 用例集结束: {} ----------------------'.format(shot_title))

        end = time.time()
        msg= '任务：%s，用时：%0.2f 秒' % (e_id, (end - start))
        log_main.info(msg)
        return  msg

    def mutli_run(self,e_id):
        try:
            msg = self.run_test_task(e_id)
            return jsonify({'status': '1', 'data': '', 'message': msg})
        except Exception as e:
            log_main.error(traceback.format_exc())
            return jsonify({'status': '0', 'data': '', 'message': traceback.format_exc()})


    # @login_required
    def get(self, e_id):

        return self.mutli_run(e_id)


