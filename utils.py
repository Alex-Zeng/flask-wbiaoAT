#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/15 11:40
# @Author  : 曾德辉
# @File    : utils.py
import os
import time
import random
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
    tt = random.randint(15000, 20000)
    if tt not in procarr:
        return tt
    else:
        getPort()


def checkPort(port):
    # 查看端口是否被占用
    s = socket.socket()
    s.settimeout(0.5)
    try:
        # s.connect_ex return 0 means port is open
        return s.connect_ex(('localhost', port)) != 0
    finally:
        s.close()


def chanJson(str):
    # str = 'title=title, type=type, loc=loc, page_id=page_id'

    str = '"' + str.replace(', ', '","').replace('=', '":"') + '"'
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


class AdbTool():
    def __init__(self):
        self._ADB = "adb"

    def restart_adb(self):
        """ restart adb server """
        subprocess.check_call([self._ADB, "kill-server"])
        subprocess.check_call([self._ADB, "start-server"])

    def is_android_device_connected_by_adb(self, device_id):
        """ return True if device connected, else return False """
        try:
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "shell", "getprop", "ro.product.model"]
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

    def adb_connect_android_device(self, device_id):
        """ return True if device connected, else return False """
        try:
            device_name = subprocess.check_output(
                [self._ADB, "connect", device_id]
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

    def input_keyevent(self, device_id, keyevent):
        """ 暂时不支持中文,支持中文需要ADB keyboard https://github.com/senzhk/ADBKeyBoard """
        try:
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "shell", "input", "keyevent", "{}".format(keyevent)]
            )
            logger.info(device_name)
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info(device_name)
        except subprocess.CalledProcessError:
            return False
        return True

    def adb_send_keys(self, device_id, content):
        """ 暂时不支持中文,支持中文需要ADB keyboard https://github.com/senzhk/ADBKeyBoard """
        try:
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "shell", "input", "text", "{}".format(content)]
            )
            logger.info(device_name)
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info(device_name)
        except subprocess.CalledProcessError:
            return False
        return True

    def home(self, device_id, ):
        self.input_keyevent(device_id, "3")

    def switch_app(self, device_id):
        self.input_keyevent(device_id, "187")

    def back(self, device_id):
        self.input_keyevent(device_id, "4")

    def install_apk(self, device_id, apk_path):
        # -g ：为应用程序授予所有运行时的权限  -t ：允许测试包 -r:覆盖安装
        try:
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "install", "-r", "-t", "-g", "{}".format(apk_path)]
            )
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info(device_name)
            if 'Success' in device_name:
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False

    def adb_push(self, device_id, remote_path):
        try:
            dst = "/data/local/tmp/tmp-{}.apk".format(int(time.time() * 1000))
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "push", "{}".format(remote_path), "{}".format(dst)]
            )
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info(device_name)
            return dst
        except subprocess.CalledProcessError:
            return False

    def adb_install_local(self, device_id, remote_path):
        local_path = self.adb_push(device_id, remote_path)
        try:
            device_name = subprocess.check_output(
                [self._ADB, "-s", device_id, "shell", "pm", "install", "-r", "-t", "-g", "{}".format(local_path)]
            )
            device_name = (
                device_name.decode('utf-8')
                    .replace("\n", "")
                    .replace("\r", "")
            )
            logger.info(device_name)

        except subprocess.CalledProcessError:
            return False
        finally:
            subprocess.check_output(
                [self._ADB, "-s", device_id, "shell", "rm", "{}".format(local_path)]
            )

adb_entity =AdbTool()
if __name__ == '__main__':
    adb = AdbTool()
    # print(adb.install_apk('IJ8LT8IFK7DUYLA6', 'C:\\Users\\Administrator\\Downloads\\wbiao_3.9.13_alpha_202005191427.apk'))
    print(adb.adb_install_local('192.168.23.2:5555',
                                'C:\\Users\\Administrator\\Downloads\\wbiao_3.9.14_alpha_202006031121.apk'))
    # print(adb.home('IJ8LT8IFK7DUYLA6'))
    # print(adb.back('127.0.0.1:7555'))
    # print(adb.adb_send_keys('IJ8LT8IFK7DUYLA6',"白啊费力"))
