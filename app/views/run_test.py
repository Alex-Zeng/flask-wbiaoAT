from flask_login import login_required
from flask_restful import Resource, reqparse
from app.models import *

parser_em = reqparse.RequestParser()
parser_em.add_argument('title', type=str, required=True, help="title cannot be blank!")


class EquipmentManagementList(Resource):
    @login_required
    def get(self):
        results = list(EquipmentManagement.query.all())
        data_list = []
        for row in results:
            data_dict = {}
            data_dict['id'] = row.id
            data_dict['title'] = row.title
            data_dict['platformName'] = row.platformName
            data_dict['platformVersion'] = row.platformVersion
            data_dict['deviceName'] = row.deviceName
            data_dict['appPackage'] = row.appPackage
            data_dict['appActivity'] = row.appActivity
            data_dict['automationName'] = row.automationName
            data_dict['noReset'] = row.noReset
            data_dict['dontStopAppOnRest'] = row.dontStopAppOnRest
            data_dict['autoGrantPermissions'] = row.autoGrantPermissions
            data_dict['systemPort'] = row.systemPort
            data_dict['remoteHost'] = row.remoteHost
            data_dict['remotePort'] = row.remotePort
            data_list.append(data_dict)
        return jsonify({'status': '1', 'data': {"page_list": data_list}, 'message': 'success'})

    @login_required
    def post(self):
        args = parser_em.parse_args()

        entity = EquipmentManagement(title=args.title, platformName=args.platformName,
                                     platformVersion=args.platformVersion,
                                     deviceName=args.deviceName, appPackage=args.appPackage,
                                     appActivity=args.appActivity, automationName=args.automationName,
                                     noReset=args.noReset, dontStopAppOnRest=args.dontStopAppOnRest,
                                     autoGrantPermissions=args.autoGrantPermissions, systemPort=args.systemPort,
                                     remoteHost=args.remoteHost, remotePort=args.remotePort)
        db.session.add(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'message': 'success'})


class EquipmentManagementDetail(Resource):
    @login_required
    def put(self, em_id):
        args = parser_em.parse_args()
        entity = EquipmentManagement.query.filter(EquipmentManagement.id == em_id).first()
        entity.title = args.title
        entity.platformName = args.platformName
        entity.platformVersion = args.platformVersion
        entity.deviceName = args.deviceName
        entity.appPackage = args.appPackage
        entity.appActivity = args.appActivity
        entity.automationName = args.automationName
        entity.noReset = args.noReset
        entity.dontStopAppOnRest = args.dontStopAppOnRest
        entity.autoGrantPermissions = args.autoGrantPermissions
        entity.systemPort = args.systemPort
        entity.remoteHost = args.remoteHost
        entity.remotePort = args.remotePort
        db.session.commit()
        return jsonify({'status': '1', 'data': {entity}, 'message': 'success'})

    @login_required
    def delete(self, em_id):
        entity = Page.query.filter(EquipmentManagement.id == em_id).first()
        db.session.delete(entity)
        db.session.commit()
        return jsonify({'status': '1', 'data': {}, 'message': 'success'})
