from flask_login import login_required
from flask_restful import Resource, reqparse
import shutil
from ext import scheduler as run_test_job
from appium_base.public.log import log_main
from utils import *
from appium_base.driver_objects import td
from appium_base.base_action import BaseAction
from appium_base.public.utils import *
from app.models import *
from appium_base.public.log import Log
import traceback
from apk import apk_path
from datetime import datetime
from sqlalchemy import func, desc
from appium_base.runtest_config import rtconf
from flask import Response, jsonify, session
from wbminitouch.deviced_object import devices

parser_em = reqparse.RequestParser()
parser_em.add_argument('title', type=str, required=True, help="title cannot be blank!")
parser_em.add_argument('rank', type=str, help="rank cannot be blank!")
parser_em.add_argument('setting_args', type=str, required=True, help="title cannot be blank!")
parser_em.add_argument('remoteHost', type=str, required=True, help="remoteHost cannot be blank!")
parser_em.add_argument('remotePort', type=str, required=True, help="remotePort cannot be blank!")
parser_em.add_argument('cron_status', type=int, help="cron_status cannot be int!")
parser_em.add_argument('cron_times', type=str, help="cron_times cannot be blank!")


class EquipmentManagementList(Resource):
    ''' 设备管理列表'''

    @staticmethod
    def scheduler_job(e_id):
        log_main.info('运行定时任务: job-{}'.format(e_id))
        with run_test_job.app.app_context():
            # 更新下次运行时间
            entity = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
            job = run_test_job.get_job(str(e_id))
            entity.next_run_time = job.next_run_time
            db.session.commit()

            # 执行真正的任务
            StartCasSuit.run_test_task(e_id)

    @staticmethod
    def add_job(e_id, cron_time):
        # 添加定时任务
        seconds, minutes, hour, day, month, year = cron_time.split(' ')
        job_id = str(e_id)
        # 任务ID如果已存在,先删除
        EquipmentManagementList.remove_job(e_id)
        job_des = {
            'id': job_id,  # 任务的唯一ID，不要冲突
            'func': __name__ + ':EquipmentManagementList.scheduler_job',  # 执行任务的function名称
            'args': [e_id],  # 如果function需要参数，就在这里添加
            'trigger': {
                'type': 'cron',
                'year': year,
                'month': month,
                'day': day,
                'hour': hour,
                'minute': minutes,
                'second': seconds
            }
        }

        try:
            run_test_job.add_job(func=job_des['func'], id=job_des['id'],
                                 args=job_des['args'], trigger=job_des['trigger'])
            current_job = run_test_job.get_job(job_des['id'])
            log_main.info('添加定时任务{}'.format(current_job))
            return current_job.next_run_time
        except Exception:
            log_main.error(traceback.format_exc())

    @staticmethod
    def remove_job(e_id):
        # 移除定时任务
        job = run_test_job.get_job(str(e_id))
        if job:
            log_main.info('移除定时任务:{}'.format(job))
            run_test_job.remove_job(str(e_id))

    # @login_required
    def get(self):
        results = list(EquipmentManagement.query.order_by(
            db.desc(EquipmentManagement.rank)).all())
        return jsonify({'status': '1', 'data': {"data_list": model_to_dict(results)}, 'message': 'success'})

    # @login_required
    def post(self):

        args = parser_em.parse_args()
        max_rank_entity = EquipmentManagement.query.order_by(db.desc(EquipmentManagement.rank)).first()
        entity = EquipmentManagement(title=args.title, setting_args=args.setting_args,
                                     rank=int(max_rank_entity.rank) + 1,
                                     remoteHost=args.remoteHost, remotePort=args.remotePort,
                                     cron_status=args.cron_status, cron_times=args.cron_times, next_run_time='')
        db.session.add(entity)

        if entity.cron_times and entity.id and entity.cron_status == 1:
            next_run_time = self.add_job(entity.id, entity.cron_times)
            entity.next_run_time = next_run_time
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'message': 'success'})


class EquipmentManagementDetail(Resource):
    ''' 设备信息'''

    def get(self, e_id):
        entity = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        max_rank_entity = EquipmentManagement.query.order_by(db.desc(EquipmentManagement.rank)).first()
        entity.rank = int(max_rank_entity.rank) + 1
        db.session.commit()

    # @login_required
    def put(self, e_id):
        args = parser_em.parse_args()
        entity = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        entity.title = args.title
        entity.rank = args.rank
        entity.setting_args = args.setting_args
        entity.remoteHost = args.remoteHost
        entity.remotePort = args.remotePort
        entity.cron_status = args.cron_status
        entity.cron_times = args.cron_times

        if args.cron_times and entity.id and args.cron_status == 1:
            next_run_time = EquipmentManagementList.add_job(e_id, entity.cron_times)
            entity.next_run_time = next_run_time
        elif args.cron_status == 0 or not args.cron_times:
            EquipmentManagementList.remove_job(e_id)
            entity.next_run_time = ''
        db.session.commit()
        return jsonify({'status': '1', 'data': args, 'message': 'success'})

    # @login_required
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
    def get(self, e_id):
        results = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        data_list = []
        for row in results.test_case_suit:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['rank'] = row.rank
            data_dict['suit_title'] = model_to_dict(row.test_case_suit).get('title', '')
            data_dict['suit_id'] = model_to_dict(row.test_case_suit).get('id', '')
            test_cases_list = []
            for item in row.test_case_suit.suit_step:
                test_cases_list.append(item.test_case)
            data_dict['test_cases'] = model_to_dict(test_cases_list)
            data_dict['update_datetime'] = str(row.update_datetime)
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

    # @login_required
    def post(self, e_id):
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
    def delete(self, e_id, es_id):
        entity = EquipmentIncludeTesSuit.query.filter(EquipmentIncludeTesSuit.id == es_id).first()
        db.session.delete(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': es_id, 'message': 'success'})


# 启动appium session
class StartSession(Resource):
    @staticmethod
    def start(e_id):
        results = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        to_dict = model_to_dict(results)
        phone_info = to_dict
        phone_info['setting_args'] = json.loads(phone_info['setting_args'])
        driver = td.start(phone_info)
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
    def post(self, project_id, case_id):
        args = parser_sc.parse_args()
        case_entity = TestCase.query.filter(TestCase.id == case_id).first()
        log_run = Log('single_case_run')
        case_list = analysis_case(case_entity.step, args.input_args)
        driver = StartSession.start(args.e_id)
        ba = BaseAction(driver, case_entity.title, log_run)
        ba.action(case_list)


# 调试用例集
class StartCasSuit(Resource):

    @staticmethod
    def run_test_task(e_id):
        entity = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        start = datetime.now()
        log_main.info('正在运行的任务：{}'.format(e_id))
        if entity.status == 1:
            raise Exception('此设备已经在运行')
        else:
            entity.status = 1
        et_title = entity.title
        tl = TestLog(equipment_id=e_id, equipment_title=et_title, equipment_args=entity.setting_args, run_test_result=2)
        db.session.add(tl)
        db.session.commit()
        tl_id = tl.id
        status = 1
        error_msg = '无'
        tl_result = 1
        failed_suit = ''
        success_suit = ''
        log_run = Log('TestLog-{}'.format(tl_id))
        log_run.info('第{}次运行,运行设备{}:{}, 参数设置:{}'.format(tl_id, e_id, et_title, entity.setting_args))
        try:
            for item in entity.test_case_suit:
                # 循环设备用例集
                driver = StartSession.start(e_id)
                suit_start = datetime.now()
                suit_title = item.test_case_suit.title
                shot_title = '{}-{}'.format(et_title, suit_title)
                log_run.info('-用例集开始: {}-'.format(shot_title))
                suit_log = TestCaseSuitLog(test_log_id=tl_id, test_case_suit_id=item.test_case_suit_id,
                                           test_case_suit_title=suit_title, run_test_result=0)
                db.session.add(suit_log)
                db.session.commit()

                suit_log_entity = TestCaseSuitLog.query.filter(TestCaseSuitLog.id == suit_log.id).first()
                try:
                    for suit_step in item.test_case_suit.suit_step:
                        # 循环用例集下的用例
                        case_start = datetime.now()
                        case_entity = suit_step.test_case

                        if suit_step.skip == 1:
                            log_run.info(
                                '-----用例{}-{},跳过'.format(case_entity.id, case_entity.title))
                            continue
                        else:
                            log_run.info(
                                '---开始:-----用例{}-{},输入参数列表: {}-----'.format(case_entity.id, case_entity.title,
                                                                            suit_step.input_args))
                        case_log_entity = TestCaseLog(test_case_id=case_entity.id, test_case_title=case_entity.title,
                                                      test_case_suit_log_id=suit_log.id)
                        db.session.add(case_log_entity)
                        db.session.commit()
                        test_case_result = 0
                        try:
                            case_step_list = analysis_case(case_entity.step, suit_step.input_args)
                            ba = BaseAction(driver, shot_title, log_run, tl_id)
                            ba.action(case_step_list, case_log_entity.id)
                            test_case_result = 1
                            log_run.info(
                                '---结束-----用例{}-{},输入参数列表: {}-----成功-------'.format(case_entity.id, case_entity.title,
                                                                                    suit_step.input_args))
                        except Exception as t:
                            test_case_result = 0
                            log_run.error(
                                '---结束-----用例{}-{},输入参数列表: {}-----失败!!!!!!!!!'.format(case_entity.id, case_entity.title,
                                                                                      suit_step.input_args))
                            # 单个用例失败
                            raise t
                        finally:
                            case_end = datetime.now()
                            case_use_time = (case_end - case_start).seconds
                            case_log_entity.run_test_case_times = case_use_time
                            case_log_entity.run_test_case_result = test_case_result
                            db.session.commit()

                    suit_log_entity.run_test_result = 1
                    success_suit += suit_title + ','

                except Exception as e:
                    suit_log_entity.run_test_result = 0
                    failed_suit += suit_title + ','
                    status = 0
                    tl_result = 0
                finally:
                    suit_end = datetime.now()
                    suit_use_time = (suit_end - suit_start).seconds
                    suit_log_entity.run_test_suit_times = suit_use_time
                    db.session.commit()
                    # 一个用例集循环结束,重新获取driver
                    driver.quit()
                    log_run.info('-用例集结束: {}, 总用时 {} 秒-'.format(shot_title, suit_use_time))
        except Exception as e:
            status = 0
            tl_result = 0
            error_msg = traceback.format_exc()
            log_main.error(error_msg)
            log_run.error(error_msg)
            raise e
        finally:
            end = datetime.now()
            run_task_use_time = (end - start).seconds
            log_entity = TestLog.query.filter(TestLog.id == tl.id).first()
            log_entity.run_test_result = tl_result
            log_entity.run_test_times = run_task_use_time
            entity.status = 0
            db.session.commit()
            msg = '此次测试执行结束,总用时:{}秒 成功用例集: [{}], 失败用例集: [{}] 错误:{}'.format(run_task_use_time, success_suit, failed_suit,
                                                                           error_msg)
            log_main.info(msg)
            log_run.info(msg)
            return jsonify({'status': status, 'data': '', 'message': msg})

    # @login_required
    def get(self, e_id):

        return self.run_test_task(e_id)


class TestLogList(Resource):
    ''' 测试报告'''

    # @login_required
    def get(self, e_id):
        results = TestCaseSuitLog.query.filter(TestCaseSuitLog.equipment_id == e_id).all()
        result_len = len(results)
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['test_case_suit_id'] = row.test_case_suit_id
            data_dict['test_case_suit_title'] = row.test_case_suit_title
            data_dict['equipment_id'] = row.equipment_id
            data_dict['equipment_title'] = row.equipment_title
            data_dict['run_test_result'] = row.run_test_result
            data_dict['run_test_suit_start_time'] = str(row.run_test_suit_start_time)
            test_cases_log_list = model_to_dict(row.test_case_log)
            data_dict['test_cases_log'] = test_cases_log_list
            data_list.append(data_dict)
        return jsonify({'status': '1', 'count': result_len, 'data': {"data_list": data_list}, 'message': 'success'})


parser_r = reqparse.RequestParser()
parser_r.add_argument('id', type=int, help="id must be num!")
parser_r.add_argument('type', type=str, required=True, help="type can not be blank")


class Report(Resource):
    ''' 测试报告'''

    def DataStatistics(self, results_count):
        data_count = {}
        data_count['false_count'] = 0
        data_count['success_count'] = 0
        for item in results_count:
            if item[0] == 0:
                data_count['false_count'] = item[1]
            else:
                data_count['success_count'] = item[1]
        data_count['total'] = data_count['false_count'] + data_count['success_count']
        return data_count

    def get_test_log_count(self):

        # 每个设备运行的日志总数
        entity = TestLog.query.order_by(desc(TestLog.run_test_start_time)).all()
        # dss['test_log_count'] = tl.__len__()
        results_count = db.session.query(TestLog.run_test_result,
                                         func.count(TestLog.id)).group_by(
            TestLog.run_test_result, ).all()
        if entity:
            data_count = self.DataStatistics(results_count)
            return data_count, model_to_dict(entity)

    def get_test_suit_log_count(self, test_log_id):
        entity = TestCaseSuitLog.query.filter(TestCaseSuitLog.test_log_id == test_log_id).all()
        results_count = db.session.query(TestCaseSuitLog.run_test_result,
                                         func.count(TestCaseSuitLog.id)).group_by(
            TestCaseSuitLog.run_test_result, TestCaseSuitLog.test_log_id).having(
            TestCaseSuitLog.test_log_id == test_log_id).all()
        if entity:
            data_count = self.DataStatistics(results_count)
            return data_count, model_to_dict(entity)

    def get_test_case_log_count(self, test_suit_log_id):
        entity = TestCaseLog.query.filter(TestCaseLog.test_case_suit_log_id == test_suit_log_id).all()
        results_count = db.session.query(TestCaseLog.run_test_case_result,
                                         func.count(TestCaseLog.id)).group_by(
            TestCaseLog.run_test_case_result, TestCaseLog.test_case_suit_log_id).having(
            TestCaseLog.test_case_suit_log_id == test_suit_log_id).all()
        if entity:
            data_count = self.DataStatistics(results_count)
            return data_count, model_to_dict(entity)

    def get_test_case_step_log_count(self, test_case_log_id):
        entity = TestCaseStepLog.query.filter(TestCaseStepLog.test_case_log_id == test_case_log_id).all()
        results_count = db.session.query(TestCaseStepLog.run_test_action_result,
                                         func.count(TestCaseStepLog.id)).group_by(
            TestCaseStepLog.run_test_action_result, TestCaseStepLog.test_case_log_id).having(
            TestCaseStepLog.test_case_log_id == test_case_log_id).all()
        if entity:
            data_count = self.DataStatistics(results_count)
            return data_count, model_to_dict(entity)

    # @login_required
    def get_all_log_data(self):
        # results = db.session.query(TestCaseLog.test_case_id,TestCaseLog.test_case_title).group_by(TestCaseLog.test_case_id,TestCaseLog.test_case_title).all()
        results = TestLog.query.all()
        data_list = []
        for item in results:
            data_dict = model_to_dict(item)
            suit_list = []
            for suit in item.test_case_suit_log:
                suit_dict = model_to_dict(suit)
                case_list = []
                for case in suit.test_case_log:
                    case_dict = model_to_dict(case)
                    case_dict['case_step_log_data_list'] = model_to_dict(case.test_case_step_log)
                    case_list.append(case_dict)
                suit_dict['case_log_data_list'] = case_list
                suit_list.append(suit_dict)
            data_dict['suit_log_data_list'] = suit_list
            data_list.append(data_dict)
        # data_list = model_to_dict(results)
        # results = model_to_dict(results)
        return data_list

    def get(self):
        args = parser_r.parse_args()
        data_count = ''
        data_list = ''
        type = args.type
        if type == 'test':
            data_count, data_list = self.get_test_log_count()
        elif type == 'suit':
            data_count, data_list = self.get_test_suit_log_count(args.id)
        elif type == 'case':
            data_count, data_list = self.get_test_case_log_count(args.id)
        elif type == 'step':
            data_count, data_list = self.get_test_case_step_log_count(args.id)
        return jsonify(
            {'status': '1', 'data': {"data_count": data_count, "data_list": data_list}, 'message': 'success'})


class getImage(Resource):
    def get(self, id):
        entity = TestCaseStepLog.query.filter(TestCaseStepLog.id == id).first()
        path = rtconf.screenShotsDir + entity.screen_shot_path

        if path:
            resp = Response(open(path, 'rb'), mimetype="image/jpeg")
            return resp


class getLogFile(Resource):

    @staticmethod
    def get_log(id):
        str = ''
        file_path = get_log_file_path(id)
        if file_path:
            with open(file_path, encoding='utf-8') as f:
                str = f.read().rstrip()
            return str

    @staticmethod
    def get_log_image_path(id):
        dir_name = 'TestLog-{}'.format(id)
        # entity = TestCaseStepLog.query.filter(TestCaseStepLog.id == id).first()
        path = rtconf.screenShotsDir

        dir_path = ''
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                if dir_name == dir:
                    dir_path = os.path.join(root, dir)
        return dir_path

    def get(self, id):
        str = ''
        file_path = get_log_file_path(id)
        if file_path:
            with open(file_path, encoding='utf-8') as f:
                str = f.read().rstrip()
            return jsonify(
                {'status': '1', 'data': str, 'message': 'success'})


class FinalLogText(Resource):
    def get(self, e_id):
        results = TestLog.query.filter(TestLog.equipment_id == e_id).order_by(
            TestLog.run_test_start_time.desc()).first()
        str = getLogFile.get_log(results.id)
        return jsonify(
            {'status': '1', 'data': str, 'message': 'success'})


class clearLog(Resource):

    def delete(self, log_id):
        entity = TestLog.query.filter(TestLog.id == log_id).first()
        ob = model_to_dict(entity)
        log_file_path = get_log_file_path(log_id)
        log_image_path = getLogFile.get_log_image_path(log_id)
        if log_file_path:
            # 删除日志运行log
            os.remove(log_file_path)
        if log_image_path:
            # 删除某次运行产生的所有截图
            shutil.rmtree(log_image_path)

        for suit in entity.test_case_suit_log:
            for case in suit.test_case_log:
                for step in case.test_case_step_log:
                    db.session.delete(step)
                db.session.delete(case)
            db.session.delete(suit)
        db.session.delete(entity)
        db.session.commit()
        return jsonify(
            {'status': '1', 'data': ob, 'message': 'success'})


parser_mini = reqparse.RequestParser()
parser_mini.add_argument('cos', type=str, action='append', help="坐标不能为空")


class operateMinitouch(Resource):

    @login_required
    def post(self, device_id):
        user = user_loader(session.get('user_id'))
        args = parser_mini.parse_args()
        cos = args.get('cos')
        cos_len = len(cos)
        flag, device = devices.get_device(user.id, user.username, device_id)

        if not flag:
            return jsonify(
                {'status': '0', 'data': '', 'message': device})

        max_x = int(device.connection.max_x)
        max_y = int(device.connection.max_y)
        if cos_len == 2:
            # 前端只有两个坐标穿过开,代表只有鼠标放开的坐标,单点击的位置
            x2 = float(cos[0])
            y2 = float(cos[1])
            tab_x = int(max_x * x2)
            tab_y = int(max_y * y2)
            # single-tap
            device.tap([(tab_x, tab_y)])
        elif cos_len == 4:
            x1 = float(cos[0])
            y1 = float(cos[1])
            x2 = float(cos[2])
            y2 = float(cos[3])
            swipe_x1 = int(max_x * x1)
            swipe_y1 = int(max_y * y1)
            swipe_x2 = int(max_x * x2)
            swipe_y2 = int(max_y * y2)
            device.swipe([(swipe_x1, swipe_y1), (swipe_x2, swipe_y2)], duration=30, pressure=50)
        return jsonify(
            {'status': '1', 'data': {'cos': cos, 'device_id': device_id}, 'message': 'success'})
        # with safe_device(device_id) as device:
        #     # It's also very important to note that the maximum X and Y coordinates may, but usually do not, match the display size.
        #     # so you need to calculate position by yourself, and you can get maximum X and Y by this way:
        #     x1,y1 = cos
        #     x = int(int(device.connection.max_x) * x1)
        #     y = int(int(device.connection.max_y) * y1)
        #     # single-tap
        #     device.tap([(x, y)])


class operaDevice(Resource):
    @login_required
    def get(self, opera, device_id):
        if opera == 'connect':
            flag = is_android_device_connected_by_adb(device_id)
            if not flag:
                flag = adb_connect_android_device(device_id)
                if not flag:
                    msg = 'adb连接{}失败,检查是否已开启adb服务,或设备已连接目标服务器,并开放了adb调试权限等'.format(device_id)
                    return jsonify(
                        {'status': 0, 'data': flag, 'message': msg})
                logger.info('adb连接{}成功'.format(device_id))
            else:
                logger.info('adb已经连接{}'.format(device_id))

            user = user_loader(session.get('user_id'))
            msg = devices.start_device(user.id, device_id)
            return jsonify(
                {'status': 1, 'data': user.username, 'message': msg})
        elif opera == 'disConnect':
            user_id = user_loader(session.get('user_id')).id
            status, msg = devices.stop_device(user_id, device_id)
            return jsonify(
                {'status': status, 'data': msg, 'message': msg})


parser_adb = reqparse.RequestParser()
parser_adb.add_argument('opera', type=int, help="操作")
parser_adb.add_argument('device_id', type=str, help="设备device_id")
parser_adb.add_argument('data', type=str, help="输入")


class AdbOperaDevice(Resource):
    def UploadFile(self):
        filename = reqparse.request.files['file']  # 获取上传的文件
        if filename:
            new_filename = apk_path + os.sep + 'wbiao.apk'
            filename.save(new_filename)  # 保存文件到指定路径
            return new_filename
        else:
            raise Exception('请上传安装包apk文件')

    @login_required
    def post(self):
        args = parser_adb.parse_args()
        opera = args.get('opera')
        device_id = args.get('device_id')
        msg = '操作错误'
        adb_entity = AdbTool()
        user = user_loader(session.get('user_id'))
        flag = devices.if_device_is_use(user.id, device_id)
        if flag == 2:
            return jsonify(
                {'status': 0, 'data': opera, 'message': "设备未连接"})
        elif flag == 0:
            return jsonify(
                {'status': 0, 'data': opera, 'message': "设备已被其他人使用"})
        try:

            if opera == 1:
                # 安装apk
                apk_path = self.UploadFile()
                adb_entity.adb_install_local(device_id, apk_path)
                msg = '安装apk成功'
            elif opera == 2:
                # 输入文本
                content = args.get('data', 0)
                adb_entity.adb_send_keys(device_id, content)
                msg = '输入文本{}成功'.format(content)
            elif opera == 3:
                # 返回键
                adb_entity.back(device_id)
                msg = '返回成功'
            elif opera == 4:
                # HOME建
                adb_entity.home(device_id)
                msg = '返回主页成功'
            elif opera == 5:
                # 后台切换应用
                adb_entity.switch_app(device_id)
                msg = '打开后台成功'
            return jsonify(
                {'status': 1, 'data': opera, 'message': msg})
        except Exception as e:
            return jsonify(
                {'status': 0, 'data': opera, 'message': e})




class AdbTool():
    def __init__(self):
        self._ADB = "adb"

    def restart_adb(self):
        """ restart adb server """
        subprocess.check_call([self._ADB, "kill-server"])
        subprocess.check_call([self._ADB, "start-server"])

    def is_android_device_connected_by_adb(self, device_id):
        """ return True if device connected, else return False """
        try:
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "shell", "getprop", "ro.product.model"]
            )
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info("device {} online".format(device_name))
        except subprocess.CalledProcessError:
            return False
        return True

    def adb_connect_android_device(self, device_id):
        """ return True if device connected, else return False """
        try:
            device_name = subprocess.check_output(
                [self._ADB, "connect", device_id]
            )
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info("device {} online".format(device_name))
            if 'cannot' in device_name:
                logger.info(device_name)
                return False
            return True
        except subprocess.CalledProcessError:
            return False

    def input_keyevent(self, device_id, keyevent):
        """ 暂时不支持中文,支持中文需要ADB keyboard https://github.com/senzhk/ADBKeyBoard """
        try:
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "shell", "input", "keyevent", "{}".format(keyevent)]
            )
            logger.info(device_name)
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info(device_name)
        except subprocess.CalledProcessError:
            return False
        return True

    def adb_send_keys(self, device_id, content):
        """ 暂时不支持中文,支持中文需要ADB keyboard https://github.com/senzhk/ADBKeyBoard """
        try:
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "shell", "input", "text", "{}".format(content)]
            )
            logger.info(device_name)
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info(device_name)
        except subprocess.CalledProcessError:
            return False
        return True

    def home(self, device_id, ):
        self.input_keyevent(device_id, "3")

    def switch_app(self, device_id):
        self.input_keyevent(device_id, "187")

    def back(self, device_id):
        self.input_keyevent(device_id, "4")

    def install_apk(self, device_id, apk_path):
        # -g ：为应用程序授予所有运行时的权限  -t ：允许测试包 -r:覆盖安装
        try:
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "install", "-r", "-t", "-g", "{}".format(apk_path)]
            )
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info(device_name)
            if 'Success' in device_name:
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False

    def adb_push(self, device_id, remote_path):
        try:
            dst = "/data/local/tmp/tmp-{}.apk".format(int(time.time() * 1000))
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "push", "{}".format(remote_path), "{}".format(dst)]
            )
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info(device_name)
            return dst
        except subprocess.CalledProcessError:
            return False

    def adb_install_local(self, device_id, remote_path):
        local_path = self.adb_push(device_id, remote_path)
        try:
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "shell", "pm", "install", "-r", "-t", "-g", "{}".format(local_path)]
            )
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info(device_name)

        except subprocess.CalledProcessError:
            return False
        finally:
            subprocess.check_output(
                [self._ADB, "-s", device_id, "shell", "rm", "{}".format(local_path)]
            )
