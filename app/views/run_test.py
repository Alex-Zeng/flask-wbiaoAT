from flask_login import login_required
from flask_restful import Resource, reqparse
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
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_dict['setting_args'] = row.setting_args
            data_dict['status'] = row.status
            data_dict['remoteHost'] = row.remoteHost
            data_dict['remotePort'] = row.remotePort
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"data_list": data_list}, 'message': 'success'})

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

class StartAppium(Resource):
    @login_required
    def post(self):
        pass