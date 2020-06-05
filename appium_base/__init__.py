#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/7/11 11:57
# @Author  : 曾德辉
# @File    : __init__.py
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)