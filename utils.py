#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/15 11:40
# @Author  : 曾德辉
# @File    : utils.py
from hashlib import sha512
from flask import request
from flask import jsonify


def get_remote_addr():
    """获取客户端IP地址"""
    address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if not address:
        address = address.encode('utf-8').split(b',')[0].strip()
    return address


def create_browser_id():
    agent = request.headers.get('User-Agent')
    if not agent:
        agent = str(agent).encode('utf-8')
    base_str = "%s|%s" % (get_remote_addr(), agent)
    h = sha512()
    h.update(base_str.encode('utf8'))
    return h.hexdigest()


if __name__ == '__main__':
    str = 'title=title, type=type, loc=loc, page_id=page_id'

    str = '"'+str.replace(', ','","').replace('=','":"')+'"'
    print(str)
