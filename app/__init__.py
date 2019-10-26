#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/15 11:59
# @Author  : 曾德辉
# @File    : __init__.py.py
from app.blue.admin import admin_bp
from app.blue.uitest import ui_test_bp
from app.blue.runtest import run_test_bp
from app.views.admin import Login, isLogin, Register, Logout, TestProject
from app.views.uitest import *
from app.views.run_test import *
from flask_restful import Api

api_admin = Api(admin_bp)
api_admin.add_resource(Login, '/login')
api_admin.add_resource(isLogin, '/islogin')
api_admin.add_resource(Register, '/register')
api_admin.add_resource(Logout, '/logout')
api_admin.add_resource(TestProject, '/projects')

api_ui_test = Api(ui_test_bp)
api_ui_test.add_resource(PageList, '/projects/<int:project_id>/pages')
api_ui_test.add_resource(PageDetail, '/projects/<int:project_id>/pages/<int:page_id>')
api_ui_test.add_resource(ElementList, '/projects/<int:project_id>/pages/<int:page_id>/elements')
api_ui_test.add_resource(ElementDetail, '/projects/<int:project_id>/pages/<int:page_id>/elements/<int:element_id>')
api_ui_test.add_resource(ActionList, '/projects/<int:project_id>/pages/<int:page_id>/actions')
api_ui_test.add_resource(ActionDetail, '/projects/<int:project_id>/pages/<int:page_id>/actions/<int:action_id>')
api_ui_test.add_resource(TestCaseList, '/projects/<int:project_id>/cases')
api_ui_test.add_resource(TestCaseDetail, '/projects/<int:project_id>/cases/<int:case_id>')
api_ui_test.add_resource(TestCaseStepList, '/projects/<int:project_id>/cases/<int:case_id>/steps')
api_ui_test.add_resource(TestCaseStepDetail, '/projects/<int:project_id>/cases/<int:case_id>/steps/<int:step_id>')
api_ui_test.add_resource(CaseSuitList, '/projects/<int:project_id>/case_suit')
api_ui_test.add_resource(CaseSuitDetail, '/projects/<int:project_id>/case_suit/<int:suit_id>')
api_ui_test.add_resource(TestSuitStepList, '/projects/<int:project_id>/case_suit/<int:suit_id>/steps')
api_ui_test.add_resource(TestSuitStepDetail, '/projects/<int:project_id>/case_suit/<int:suit_id>/steps/<int:step_id>')
api_ui_test.add_resource(FunctionList, '/functions')
api_ui_test.add_resource(FunctionDetail, '/functions/<int:function_id>')

api_run_test = Api(run_test_bp)

api_run_test.add_resource(EquipmentManagementList, '/equipment')
api_run_test.add_resource(EquipmentManagementDetail, '/equipment/<int:e_id>')
api_run_test.add_resource(StartSession, '/equipment/<int:e_id>/start')
api_run_test.add_resource(StopSession, '/equipment/<int:e_id>/stop')