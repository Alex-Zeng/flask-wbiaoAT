#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/15 11:56
# @Author  : 曾德辉
# @File    : main.py
from flask import Flask
from app.blue.admin import admin_bp
from app.blue.uitest import ui_test_bp

from config import DevConfig
from ext import db, login_manager
from flask_cors import CORS


app = Flask(__name__)  # __name__ : main
CORS(app, supports_credentials=True)  # 解决前后端分离的  跨域问题
app.config.from_object(DevConfig)
db.init_app(app)
login_manager.init_app(app)

# app.add_url_rule("/", view_func=views.index)
app.register_blueprint(admin_bp,url_prefix='/admin')
app.register_blueprint(ui_test_bp,url_prefix='/uitest')


if __name__ == '__main__':
    app.run(port=5002)
    
