#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/15 11:40
# @Author  : 曾德辉
# @File    : utils.py
import os
import random
import socket
from hashlib import sha512

from flask import request


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

def getPort():
    # 获取一个可用端口
    pscmd = "netstat -ntl |grep -v Active| grep -v Proto|awk '{print $4}'|awk -F: '{print $NF}'"
    procs = os.popen(pscmd).read()
    procarr = procs.split("\n")
    tt= random.randint(15000,20000)
    if tt not in procarr:
        return tt
    else:
        getPort()

def checkPort(port):
    # 查看端口是否被占用
    s = socket.socket()
    s.settimeout(0.5)
    try:
        #s.connect_ex return 0 means port is open
        return s.connect_ex(('localhost', port)) != 0
    finally:
        s.close()

def chanJson(str):
    # str = 'title=title, type=type, loc=loc, page_id=page_id'

    str = '"'+str.replace(', ','","').replace('=','":"')+'"'
    return str

if __name__ == '__main__':
    print(getPort())