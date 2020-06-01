#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/15 11:40
# @Author  : 曾德辉
# @File    : utils.py
import os
import random
import socket
from hashlib import sha512
import requests
import tempfile
import socket
import subprocess
from wbminitouch import config
from wbminitouch.logger import logger
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

def str2byte(content):
    """ compile str to byte """
    return content.encode(config.DEFAULT_CHARSET)


def download_file(target_url):
    """ download file to temp path, and return its file path for further usage """
    resp = requests.get(target_url)
    with tempfile.NamedTemporaryFile("wb+", delete=False) as f:
        file_name = f.name
        f.write(resp.content)
    return file_name


def is_port_using(port_num):
    """ if port is using by others, return True. else return False """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    try:
        result = s.connect_ex((config.DEFAULT_HOST, port_num))
        # if port is using, return code should be 0. (can be connected)
        return result == 0
    finally:
        s.close()


def restart_adb():
    """ restart adb server """
    _ADB = config.ADB_EXECUTOR
    subprocess.check_call([_ADB, "kill-server"])
    subprocess.check_call([_ADB, "start-server"])


def is_android_device_connected_by_adb(device_id):
    """ return True if device connected, else return False """
    try:
        device_name = subprocess.check_output(
            ['adb', "-s", device_id, "shell", "getprop", "ro.product.model"]
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

def adb_connect_android_device(device_id):
    """ return True if device connected, else return False """
    try:
        device_name = subprocess.check_output(
            ['adb', "connect", device_id]
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



if __name__ == '__main__':
    print(is_android_device_connected_by_adb('127.0.0.1:7555'))
