#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/7/1 15:42
# @Author  : 曾德辉
# @File    : utils.py
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import allure
from functools import wraps
import datetime
import collections
from base.runtest_config import rtconf
def all_file_path(root_directory, extension_name):
    '''
    遍历目录
    :param root_directory: 目录
    :param extension_name: 文件扩展名
    :return:
    '''
    file_dic = collections.OrderedDict()
    for parent, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            if 'filter' not in filename:
                if filename.endswith(extension_name):
                    path = os.path.join(parent, filename).replace('\\', '/')
                    file_dic[filename] = path

    return file_dic


def monitorapp(function):
    """
     用例装饰器，截图，日志，是否跳过等
     获取系统log，Android logcat、ios 使用syslog
    """

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        try:
            allure.dynamic.description('用例开始时间:{}'.format(datetime.datetime.now()))
            function(self, *args, **kwargs)
            self.driver.get_log('logcat')
        except Exception as E:
            f = self.driver.get_screenshot_as_png()
            allure.attach(f, '失败截图', allure.attachment_type.PNG)
            logcat = self.driver.get_log('logcat')
            c = '\n'.join([i['message'] for i in logcat])
            allure.attach(c, 'APPlog', allure.attachment_type.TEXT)
            raise E

    return wrapper


def excute_cmd_result(command):
    """
    执行cmd命令并返回结果
    :param command:
    :return: 输出结果result_list
    """
    result_list = []
    result = os.popen(command).readlines()
    for i in result:
        if i == '\n':
            continue
        result_list.append(i.strip('\n'))
    return result_list


def excute_cmd(command):
    """
    执行cmd命令,不返回结果
    """
    os.system(command)


def port_is_used(port_num):
    '''
    判断端口是否被占用
    '''
    flag = None
    command = 'netstat -ano | findstr ' + str(port_num)
    result = excute_cmd_result(command)
    if len(result) > 0:
        flag = True
    else:
        flag = False
    return flag


def create_port_list(start_port, device_list):
    '''start_port 4701
    生成可用端口
    @parameter start_port
    @parameter device_list
    '''
    port_list = []
    if device_list != None:
        while len(port_list) != len(device_list):
            if port_is_used(start_port) != True:
                port_list.append(start_port)
            start_port = start_port + 1
        return port_list
    else:
        print("生成可用端口失败")
        return None


def get_devices():
    '''
    获取设备信息
    '''
    pass


def get_platformVersion():
    """
    :return: 手机版本号
    """
    pass


def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return False

# 解析用例
def analysis_case(steps, case_args):
    step_list = []
    case_args_dict={}
    try:
        if case_args:
            case_args_dict = json.loads(case_args)
    except Exception:
        return '参数非法: 不符合json格式,请仔细检查参数'

    if case_args_dict:
        for k,v in case_args_dict.items():
            if isinstance(v,list):
                case_args_dict[k] = collections.deque(v)
            else:
                return '参数非法: 值不是列表形式'
    for item in steps:
        case_step_dict = {}
        case_step_dict['step'] = item.rank
        case_step_dict['skip'] = item.skip
        case_step_dict['title'] = item.title
        case_step_dict['case_step'] = '步骤: {}'.format(item.rank)
        case_step_dict['action'] = item.action.fun.fun_title
        case_step_dict['type_for_android'] = item.action.ele.type_for_android
        case_step_dict['type_for_ios'] = item.action.ele.type_for_ios
        case_step_dict['element_loc_for_android'] = item.action.ele.loc_for_android
        case_step_dict['element_loc_for_ios'] = item.action.ele.loc_for_ios
        case_step_dict['element_info'] = item.action.ele.title
        case_step_dict['screen_shot'] = item.take_screen_shot
        case_step_dict['wait_time'] = item.wait_time
        case_step_dict['output_arg'] = item.output_key
        if item.input_key:
            try:
                case_step_dict['input_arg'] = case_args_dict.get(item.input_key).popleft()
                case_step_dict['input_key'] = item.input_key
            except:
                pass
                # return '未找到对应参数'
        else:
            case_step_dict['input_arg'] = ''
        step_list.append(case_step_dict)
    return step_list

def get_log_file_path(id):
    file_name = 'TestLog-{}.log'.format(id)
    # entity = TestCaseStepLog.query.filter(TestCaseStepLog.id == id).first()
    path = rtconf.logDir

    file_path = ''
    for root, dirs, files in os.walk(path):
        for f in files:
            if file_name == f:
                file_path = os.path.join(root, f)
    return file_path

if __name__ == '__main__':
    # print(os.path.abspath(os.path.join(os.path.dirname(__file__))
    print(os.path.abspath(__file__))
    print(os.getcwd())
