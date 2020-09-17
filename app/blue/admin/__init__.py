#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/15 11:57
# @Author  : 曾德辉
# @File    : __init__.py.py
from flask import Blueprint

admin_bp = Blueprint('admin',__name__,template_folder='templates',static_folder='static')

