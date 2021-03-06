#!/usr/bin/python3
# @Time    : 2019/6/28 14:08
# @Author  : 曾德辉
# @File    : base_action.py

import os
import re
import time
import traceback
from datetime import datetime
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

from app.models import TestCaseStepLog
from appium_base.runtest_config import rtconf
from ext import db


class BaseAction:

    def __init__(self, driver, case_title, run_log, tl_id='debug'):
        self.driver = driver
        self._by_type = rtconf.find_ele_types
        self.current_case = dict()
        self.log = run_log
        self.ele_wait_time = rtconf.find_ele_wait_time
        self.screen_shot_wait_time = rtconf.take_screen_shot_wait_time
        self.screen_shot_folder_title = case_title
        self.screen_shot_folder_log_id = 'TestLog-{}'.format(tl_id)
        self.assert_result = ''

    def action(self, case_step_list, case_log_id=None):
        """
        循环执行用例集中每条用例对应的action方法
        """

        error_msg = ''
        result = 0
        test_data = {}
        for v in case_step_list:
            start_time = datetime.now()
            self.current_case = v
            self.assert_result = ''
            step_rank = v['step']
            step_skip = v['skip']
            case_step = v['case_step']
            wait_time = v['wait_time']
            step_title = v['title']
            action = v['action']
            type_for_android = v['type_for_android']
            type_for_ios = v['type_for_ios']
            screenshot = v['screen_shot']
            element_info = v['element_info']
            element_loc_for_ios = v['element_loc_for_ios']
            element_loc_for_android = v['element_loc_for_android']
            input_data = v.get('input_arg', None)
            input_key = v.get('input_key', None)
            output_data = v['output_arg']
            screen_shot_path = ''

            try:
                # 步骤跳过
                if step_skip:
                    self.log.info(
                        '---------- {} --- {} 此用例跳过'.format( case_step,step_title))
                    continue

                # 判断平台 ios 则loc  find_type不一样,前端同一个元素下面维护 Android和ios的元素查找方式和位置
                if self.driver.desired_capabilities.get('platform', '') == 'MAC':
                    loc = self._by_type.get(type_for_ios, ''), element_loc_for_ios
                else:
                    loc = self._by_type.get(type_for_android, ''), element_loc_for_android

                # 是否引用前面某个用例的 输出值,以xx开头
                if input_data.startswith(rtconf.use_output_arg_symbol):
                    input_data = test_data[input_data[len(rtconf.use_output_arg_symbol):]]

                if wait_time:
                    time.sleep(wait_time)
                if loc[0]:
                    if input_data:
                        output_text = self.__getattribute__(action)(loc, input_data)
                    else:
                        output_text = self.__getattribute__(action)(loc)
                else:
                    output_text = self.__getattribute__(action)()

                if output_data == 'verify_code':
                    # 测试环境验证码,只匹配数字
                    pattern = re.compile('\d{6}')
                    output_text = pattern.search(output_text).group()
                    # 输处返回参数，给依赖用例使用
                    test_data[output_data] = output_text
                    self.log.info("处理验证码关键字verify_code,从验证码toast中得到验证码:{}".format(output_text))
                else:
                    test_data[output_data] = output_text

                self.log.info(
                    '√√√{}-{}-{} --- {} --- {}---输入参数: **{}** - 输出参数:**{}**'.format('成功', case_step,
                                                                                    step_title, element_info,
                                                                                    self.assert_result,
                                                                                    input_data, output_text))
                # 截图
                if screenshot:
                    shot_name = '步骤_{}_{}'.format(step_rank, step_title)
                    screen_shot_path = self.take_screen_shot(name=shot_name)
                result = 1
            except Exception as e:
                result = 0
                self.log.error('×××{}:{}{} --- {} --- {}---输入参数: **{}**'.format('错误',
                                                                                case_step,
                                                                                step_title,
                                                                                element_info,
                                                                                self.assert_result,
                                                                                input_data,
                                                                                ))
                error_msg = traceback.format_exc()
                self.log.error(error_msg)
                err_shot_name = '步骤_{}_{}错误截图'.format(step_rank, step_title)
                screen_shot_path = self.take_screen_shot(name=err_shot_name)
                raise e
            finally:
                end_time = datetime.now()
                run_test_case_step_times = (end_time - start_time).seconds
                action_output = ''
                if output_data:
                    action_output = '{}:{}'.format(output_data, test_data[output_data])
                action_input = ''
                if input_data:
                    action_input = '{}:{}'.format(input_key, input_data)
                if case_log_id:
                    entity = TestCaseStepLog(test_case_log_id=case_log_id,
                                             test_case_step_rank=step_rank,
                                             test_case_action_title=step_title, test_case_action_input=action_input,
                                             test_case_action_output=action_output,
                                             run_test_action_result=result, error_msg=error_msg,
                                             action_start_time=start_time, action_end_time=end_time,
                                             run_test_case_times=run_test_case_step_times,
                                             screen_shot_path=screen_shot_path)
                    db.session.add(entity)
                    db.session.commit()

    def click(self, loc):
        """
        点击
        """
        self.find_element(loc).click()

    def clear_text(self, loc):
        """
        清除文本
        """
        self.find_element(loc).clear()

    def input_text(self, loc, input_data):
        """
        输入文本
        """
        self.log.info("输入参数:{}".format(input_data))
        self.find_element(loc).send_keys(input_data)

    def get_element_text(self, loc):
        """
        获取元素文本
        """
        return self.find_element(loc).get_attribute("text")

    def check_element(self, loc):
        """
        断言元素存在
        """
        try:
            assert self.find_element(loc)
            self.assert_result = '断言成功-----找到{}元素，截图保留'.format(loc)
        except Exception as e:
            self.assert_result = '断言失败-----未找到元素{}'.format(loc)
            raise e

    def check_not_element(self, loc):
        """
        断言元素不存存在
        """
        try:
            el = self.find_element(loc)
            if el:
                self.assert_result = '断言失败-----{}元素存在'.format(loc)
                raise Exception('断言失败-----{}元素存在'.format(loc))
        except Exception as e:
            self.assert_result = '断言成功-----{}元素不存在'.format(loc)

    def check_text(self, loc, input_data):
        """
         判断文本是否相等
        """
        assert_text = self.get_element_text(loc)
        try:
            assert input_data in assert_text
            self.assert_result = '断言成功-----文本{}存在于{}'.format(input_data, assert_text)
        except Exception as e:
            self.assert_result = '断言失败-----文本{}不存在于{}'.format(input_data, assert_text)
            raise e

    def check_elements(self, loc):
        """
        断言元素（多个）是否存在
        """
        try:
            assert self.find_elements(loc)
            self.assert_result = '断言成功-----成功找到{}元素，截图保留'.format(loc)
        except Exception as e:
            self.assert_result = '断言失败-----未找到元素{}'.format(loc)
            raise e

    def check_activity(self, loc, input_data):
        """
        检查是否activity是否符合预期
        """
        expect_activity = input_data
        cur_activity = self.driver.current_activity
        try:
            assert cur_activity == expect_activity
            self.assert_result = '断言成功-----预期页面，截图保留'.format(loc)
            return 'current_activity: {}, -- expect_activity: {}'.format(cur_activity, expect_activity)
        except Exception as e:
            self.assert_result = '断言失败-----非预期页面{}'.format(expect_activity)
            raise e

    def get_page_source(self):
        """
        得到当前页面源文件
        """
        case_path = rtconf.pageSourceDir + os.sep + self.driver.current_activity + '.xml'

        if not os.path.exists(case_path):
            f = open(case_path, 'w', encoding='utf-8')
            f.write(self.driver.page_source)
            f.close()

    def back(self):
        """
        后退
        """
        time.sleep(1)
        self.driver.back()

    def move_away_el(self, loc):
        """
        移开某个元素，防止遮挡
        :return:
        """
        try:
            el = self.find_element(loc)
            end_x = el.size.get('x')
            end_y = el.size.get('y')
            touch_action = TouchAction(self.driver)
            touch_action.long_press(el).move_to(x=end_x, y=end_y).release().perform()
        except Exception:
            self.log.info('没有这个元素')

    def over(self):
        """
        退出
        """
        self.driver.quit()

    def get_size(self):
        """
        获取界面大小
        """
        x = self.driver.get_window_size()['width']
        y = self.driver.get_window_size()['height']
        return x, y

    def if_element_exist_then_close(self, loc):
        """
        如果元素存在则点击,否则忽略
        """
        try:
            self.find_element(loc, wait_time=5).click()

        except Exception:

            self.log.info("没有浮窗广告")
            return "没有浮窗广告"

    def wait(self, input_data):
        """
        等待几秒(传整数参数))
        """
        s = 3  # 默认三秒
        time.sleep(s if not input_data else input_data)

    def get_contexts(self):
        """
        获取contexts
        """
        contexts = self.driver.contexts
        self.log.info(contexts)
        return contexts

    def get_current_context(self):
        """
        获取当前context
        """
        context = self.driver.context
        self.log.info(context)
        return context

    def switch_to_webview(self, input_data):
        """
        切换到webview或者最后一个webview
        """
        contexts = self.get_contexts()
        if input_data and input_data in contexts:
            self.driver.switch_to.context(input_data)
        else:
            self.driver.switch_to.context(contexts[-1])

    def get_current_window_handle(self):
        """
        获取当前window_handle
        """
        return self.driver.current_window_handle

    def switch_window_handle(self, input_data):
        """
        切换window_handles或者最后一个handle
        """
        window_handles = self.driver.window_handles()
        if input_data and input_data in window_handles:
            self.driver.switch_to.window(input_data)
        else:
            self.driver.switch_to.window(window_handles[-1])

    def switch_to_native_app(self):
        """
        切换到native
        """
        self.driver.switch_to.context('NATIVE_APP')

    def swipe_to_up(self):
        """
        向上滑动屏幕
        """
        screen_size = self.get_size()
        x1 = int(screen_size[0] * 0.5)

        # %60的距离,相当于滑动一页
        y1 = int(screen_size[1] * 0.8)
        y2 = int(screen_size[1] * 0.2)
        self.driver.swipe(x1, y1, x1, y2, 1000)

    def swipe_to_down(self):
        """
        向下滑动屏幕
        """
        screen_size = self.get_size()
        x1 = int(screen_size[0] * 0.5)
        # %50的距离,相当于滑动一页
        y1 = int(screen_size[1] * 0.3)
        y2 = int(screen_size[1] * 0.9)
        self.driver.swipe(x1, y1, x1, y2, 1000)

    def swipe_to_right(self):
        """
        向右滑动屏幕
        """
        screen_size = self.get_size()
        x1 = int(screen_size[0] * 0.2)
        y1 = int(screen_size[1] * 0.5)
        x2 = int(screen_size[1] * 0.8)
        self.driver.swipe(x1, y1, x2, y1, 1000)

    def swipe_to_left(self):
        """
        向左滑动屏幕
        """
        screen_size = self.get_size()
        x1 = int(screen_size[0] * 0.8)
        y1 = int(screen_size[1] * 0.5)
        x2 = int(screen_size[1] * 0.2)
        self.driver.swipe(x1, y1, x2, y1, 1000)

    def long_press(self, loc):
        """
        长按元素
        """
        ele = self.find_element(loc)
        TouchAction(self.driver).long_press(ele).perform()

    def tap_by_coordinates(self, loc):
        """
        点击坐标
        """
        find_type, proportional = loc
        x, y = proportional.split('|')
        TouchAction(self.driver).tap(x=x, y=y).perform()

    def tap_by_proportional(self, loc):
        """
        按屏幕比例点击坐标
        """
        print(loc)
        find_type, proportional = loc
        x, y = proportional.split('|')
        width, height = self.get_size()
        print('当前屏幕大小为: {}*{}'.format(width, height))
        x = int(float(x) * width)
        y = int(float(y) * height)
        print('当前点击坐标为x:{} , y:{}'.format(x, y))
        TouchAction(self.driver).tap(x=x, y=y).perform()

    def refresh(self):
        """
        刷新
        """
        self.driver.refresh()

    def press_enter(self):
        """
        按下回车键
        """
        self.driver.keyevent(66)

    @staticmethod
    def execute_adb_cmd(input_data):
        """
        执行adb命令
        """
        os.system(input_data)

    def find_element(self, loc, wait_time=None):
        """
        查找符合的元素并返回
        return: 元素对象
        """
        by = loc[0]
        value = loc[1]
        ewt = 3  # element_wait_time
        if wait_time:
            ewt = wait_time
        else:
            ewt = self.ele_wait_time

        try:
            if by == MobileBy.XPATH:
                value = self.make_xpath_with_feature(value)
            return WebDriverWait(self.driver, ewt, 1).until(lambda x: x.find_element(by, value))
        except TimeoutException:
            err_msg = '错误信息: {}秒内未找到该元素, 查询方式: {}, 元素位置: {}'.format(ewt, by, value)
            raise TimeoutException(err_msg)

    def find_elements(self, loc, wait_time=None):
        """
        查找所有符合预期的元素元素
        return: 元素对象列表
        """
        by = loc[0]
        value = loc[1]

        ewt = 3  # element_wait_time
        if wait_time:
            ewt = wait_time
        else:
            ewt = self.ele_wait_time

        try:
            if by == MobileBy.XPATH:
                value = self.make_xpath_with_feature(value)
            return WebDriverWait(self.driver, ewt, 1).until(lambda x: x.find_elements(by, value))
        except TimeoutException:
            err_msg = '错误信息: {}秒内未找到该元素, 查询方式: {}, 元素位置: {}'.format(ewt, by, value)
            s_jpg = self.driver.get_screenshot_as_png()
            raise TimeoutException(err_msg, s_jpg, traceback.format_exc())

    def to_activity(self, loc, input_data):
        """
        启动activity
        """
        app_package = self.driver.desired_capabilities().get('appPackage')
        self.driver.start_activity(app_package, input_data)

    def back_to_some_activity(self, loc, activity):
        """一直点手机返回按键返回主页"""

        for i in range(10):
            self.back()
            if self.driver.current_activity == activity:
                break

    def back_until_element_show(self, loc):
        """一直点手机返回按键直到某个元素出现"""

        for i in range(10):
            self.back()
            try:
                if self.find_element(loc, wait_time=3):
                    break
            except Exception:
                pass

    def travel_elements(self, loc):
        """
        遍历元素,点击,返回两个操作
        """
        elements = self.find_elements(loc)
        for i in range(len(elements)):
            self.find_elements(loc)[i].click()
            time.sleep(1)
            pagename = "元素{}点击后".format(i)
            self.take_screen_shot(name=pagename)

    def take_screen_shot(self, name='截图', wait_time=None):
        """
        method explain:获取当前屏幕的截图
        parameter explain：【name】 截图的名称
        Usage:
            device.take_screenShot(u"个人主页")   #实际截图保存的结果为：20180113171058个人主页.png
        """
        # day = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        tm = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        fq = rtconf.screenShotsDir + os.sep + self.screen_shot_folder_log_id + os.sep + self.screen_shot_folder_title
        file_title = tm + '{}.png'.format(name)
        if not os.path.exists(fq):
            os.makedirs(fq)
        filename = fq + os.sep + file_title
        print(filename)
        time.sleep(wait_time if wait_time else self.screen_shot_wait_time)
        result = self.driver.get_screenshot_as_file(filename)
        print("截图成功或失败:%s" % result)
        # temp_path 用于解耦,保存到数据库日志的截图路径,以后项目目录改变可以方便拼接完整路径
        temp_path = os.sep + self.screen_shot_folder_log_id + os.sep + self.screen_shot_folder_title + os.sep + file_title
        return temp_path

    @staticmethod
    def make_xpath_with_unit_feature(loc):
        """
        拼接feature中间的部分
        """
        key_index = 0
        value_index = 1
        option_index = 2
        feature = ""
        args = loc.split(",")

        if len(args) == 2:
            feature = "contains(@" + args[key_index] + ",'" + args[value_index] + "')"
        elif len(args) == 3:
            if args[option_index] == "1":
                feature = "@" + args[key_index] + "=" + args[value_index] + "'"
            elif args[option_index] == "0":
                feature = "contains(@" + args[key_index] + ",'" + args[value_index] + "')"

        return feature

    def make_xpath_with_feature(self, loc):
        """
        loc:xpath
        Usage:
            make_xpath_with_feature("text,首页")   #输出结果为："//*[contains(@text,'首页')]"
            make_xpath_with_feature("text,首页,1")   #输出结果为："//*[@text='首页']"
            make_xpath_with_feature("text,首页")   #输出结果为："//*[contains(@text,'首页')]"
        """
        feature_start = "//*["
        feature_end = "]"
        feature = ""
        if isinstance(loc, str):
            # 直接传xpath
            if loc.startswith("//") or loc.startswith("(//"):
                return loc
            elif '&' in loc:
                # loc 包含 & 即多条件 By.XPATH, "resource-id,com.wbiao.wbauction:id/select"&"text,镖哭"
                for i in loc.split('&'):
                    feature += self.make_xpath_with_unit_feature(i) + ' and '

            else:
                # loc 是 字符串即单条件 resource-id,com.wbiao.wbauction:id/select

                feature = self.make_xpath_with_unit_feature(loc)

        feature = feature.rstrip(' and ')
        loc = feature_start + feature + feature_end
        return loc


if __name__ == '__main__':
    pass
