#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/7/24 9:13
# @Author  : 曾德辉
# @File    : log.py
#coding=utf-8
#author='Shichao-Dong'
import time,os
import logging
from base.public.utils import mkdir
from base.runtest_config import rtconf


log_path = rtconf.logDir
mkdir(log_path)

class Log():

    def __init__(self, file):

        filename =  file +''.join('.log') #设置log名
        self.logname =os.path.join(log_path,filename)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        #设置日志输出格式
        self.formatter = logging.Formatter('%(levelname)s - [%(asctime)s] - %(message)s')

    def output(self,level,message):
        '''
        :param level: 日志等级
        :param message: 日志需要打印的信息
        :return:
        '''

        #send logging output to a disk file
        fh = logging.FileHandler(self.logname,'a',encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        #send logging output to streams
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

        if level == 'info':
            self.logger.info(message)
        elif level =='debug':
            self.logger.debug(message)
        elif level =='warn':
            self.logger.warning(message)
        elif level =='error':
            self.logger.error(message)

        #防止重复打印
        self.logger.removeHandler(fh)
        self.logger.removeHandler(ch)

        fh.close()

    def info(self,message):
        self.output('info',message)

    def debug(self,message):
        self.output('debug',message)

    def warn(self,message):
        self.output('warn',message)

    def error(self,message):
        self.output('error',message)

log_main = Log('main')
log_err = Log('err')