import threading

from flask_login import login_required
from flask_restful import Resource, reqparse
import json
from app.blue.runtest.base.base_driver import BaseDriver
from app.blue.runtest.base.driver_objects import td
from app.models import *

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
parser_ap = reqparse.RequestParser()
parser_ap.add_argument('session_id', type=str, required=True, help="session_id cannot be blank!")


class StartSession(Resource):
    # @login_required
    def get(self, e_id):
        results = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        phone_info = model_to_dict(results)
        phone_info['setting_args'] = json.loads(phone_info['setting_args'])
        driver = td.start(phone_info)
        results.status = 1
        results.session_id = driver.session_id
        db.session.commit()
        return jsonify({'status': '1', 'data': driver.session_id, 'message': 'success'})


# 停止appium session
class StopSession(Resource):
    # @login_required
    def post(self, e_id):
        args = parser_ap.parse_args()
        results = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        results.status = 0
        results.session_id = ''
        db.session.commit()
        msg = td.quit(args.session_id)
        return jsonify({'status': '1', 'data': args.session_id, 'message': msg})


# 调试单个用例
class StartCase(Resource):
    # @login_required
    def get(self, e_id):
        entity = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        print(entity)


# 调试用例集
class StartCasSuit(Resource):
    # @login_required
    def get(self, e_id):
        entity = EquipmentManagement.query.filter(EquipmentManagement.id == e_id).first()
        print(entity)
