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
from base.runtest_config import rtconf
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
            step_rank = v['step']
            step_skip = v['skip']

            case_step = v['case_step']
            wait_time = v['wait_time']
            action_title = v['action_title']
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

            # 判断平台 ios 则loc  find_type不一样,前端同一个元素下面维护 Android和ios的元素查找方式和位置
            if self.driver.desired_capabilities.get('platform','') == 'MAC':
                loc = self._by_type.get(type_for_ios, ''), element_loc_for_ios
            else:
                loc = self._by_type.get(type_for_android, ''), element_loc_for_android
            # 是否引用前面某个用例的 输出值
            if input_data.startswith(rtconf.use_output_arg_symbol):
                input_data = test_data[input_data[len(rtconf.use_output_arg_symbol):]]

            if step_skip:
                self.log.info(
                    '----------{}: {} --- {} --- {}---输入参数: {} ----输出参数: ----------'.format('成功', case_step,
                                                                                             action_title, element_info,
                                                                                             input_data))
                continue

            try:
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
                else:
                    test_data[output_data] = output_text

                self.log.info(
                    '----------{}: {} --- {} --- {}---输入参数: {} ----输出参数:{}----------'.format('成功', case_step,
                                                                                             action_title, element_info,
                                                                                             input_data, output_text))
                # 截图
                if screenshot:
                    shot_name = '步骤_{}_{}'.format(step_rank,action_title)
                    screen_shot_path = self.take_screen_shot(name=shot_name)
                result = 1
            except Exception as e:
                result = 0
                output_text = 'output_text'
                self.log.error('!!!!!!!!!{}: {} --- {} --- {}---输入参数: {} ----输出参数:错误!!!!!!!!!'.format('错误', case_step,
                                                                                                      action_title,
                                                                                                      element_info,
                                                                                                      input_data,
                                                                                                      ))
                error_msg = traceback.format_exc()
                self.log.error(error_msg)
                err_shot_name = '步骤_{}_{}错误截图'.format(step_rank, action_title)
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
                                             test_case_action_title=action_title, test_case_action_input=action_input,
                                             test_case_action_output=action_output,
                                             run_test_action_result=result, error_msg=error_msg,
                                             action_start_time=start_time, action_end_time=end_time,
                                             run_test_case_times=run_test_case_step_times,screen_shot_path=screen_shot_path)
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
        self.find_element(loc).send_keys(input_data)

    def get_element_text(self, loc):
        """
        获取元素文本
        """
        return self.find_element(loc).get_attribute("text")

    def check_element(self, loc):
        """
        断言元素是否存在
        """
        try:
            assert self.find_element(loc)
            self.take_screen_shot(name='断言成功')
            self.log.info('成功找到{}元素，截图保留'.format(loc))
        except Exception as e:
            self.log.error('断言失败未找到元素{}'.format(loc))
            self.take_screen_shot(name='断言失败')
            self.log.info('未找到{}元素，截图保留'.format(loc))
            raise e

    def check_text(self, loc, input_data):
        """
         判断文本是否相等
        """
        assert input_data in self.find_element(loc).get_attribute("text")
        self.log.info('断言成功:文本{} 存在'.format(input_data))

    def check_elements(self, loc):
        """
        断言元素（多个）是否存在
        """
        try:
            assert self.find_elements(loc)
            self.take_screen_shot(name='断言成功')
            self.log.info('成功找到{}元素，截图保留'.format(loc))
            self.log.info('断言成功')
        except Exception as e:
            self.log.error('断言失败未找到元素{}'.format(loc))
            self.take_screen_shot(name='断言失败')
            self.log.info('未找到{}元素，截图保留'.format(loc))
            raise e

    def check_activity(self, loc, input_data):
        """
        检查是否activity是否符合预期
        """
        expect_activity = input_data
        cur_activity = self.driver.current_activity
        try:
            assert cur_activity == expect_activity
            self.take_screen_shot(name='断言成功预期页面')
            self.log.info('预期页面，截图保留'.format(loc))
            self.log.info('是预期页面')
            return 'current_activity: {}, -- expect_activity: {}'.format(cur_activity, expect_activity)
        except Exception as e:
            self.log.error('断言失败:非预期页面{}'.format(expect_activity))
            self.take_screen_shot(name='断言失败非预期页面')
            self.log.info('非预期页面，截图保留'.format(loc))
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

    def if_dialog_close(self, loc):
        """
        关闭浮窗广告
        """
        try:
            self.find_element(loc).click()

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
        y1 = int(screen_size[1] * 0.7)
        y2 = int(screen_size[1] * 0.1)
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

    def find_element(self, loc):
        """
        查找符合的元素并返回
        return: 元素对象
        """
        by = loc[0]
        value = loc[1]
        try:
            if by == MobileBy.XPATH:
                value = self.make_xpath_with_feature(value)
            return WebDriverWait(self.driver, self.ele_wait_time, 1).until(lambda x: x.find_element(by, value))
        except TimeoutException:
            err_msg = '错误信息: {}秒内未找到该元素, 查询方式: {}, 元素位置: {}'.format(self.ele_wait_time, by, value)
            raise TimeoutException(err_msg)

    def find_elements(self, loc):
        """
        查找所有符合预期的元素元素
        return: 元素对象列表
        """
        by = loc[0]
        value = loc[1]
        try:
            if by == MobileBy.XPATH:
                value = self.make_xpath_with_feature(value)
            return WebDriverWait(self.driver, self.ele_wait_time, 1).until(lambda x: x.find_elements(by, value))
        except TimeoutException:
            err_msg = '错误信息: {}秒内未找到该元素, 查询方式: {}, 元素位置: {}'.format(self.ele_wait_time, by, value)
            s_jpg = self.driver.get_screenshot_as_png()
            raise TimeoutException(err_msg, s_jpg, traceback.format_exc())

    def to_activity(self, input_data):
        """
        启动activity
        """
        app_package = self.driver.desired_capabilities().get('appPackage')
        self.driver.start_activity(app_package, input_data)

    def travel_elements(self, loc):
        """
        遍历元素,点击,返回两个操作
        """
        elements = self.find_elements(loc)
        before_click_activity = self.driver.current_activity
        for i in range(len(elements)):
            self.find_elements(loc)[i].click()
            time.sleep(1)
            pagename = "元素{}点击后".format(i)
            self.take_screen_shot(name=pagename)
            if before_click_activity != self.driver.current_activity:
                self.back()

    def take_screen_shot(self, name='截图', wait_time=None):
        """
        method explain:获取当前屏幕的截图
        parameter explain：【name】 截图的名称
        Usage:
            device.take_screenShot(u"个人主页")   #实际截图保存的结果为：20180113171058个人主页.png
        """
        # day = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

        fq = rtconf.screenShotsDir + os.sep + self.screen_shot_folder_log_id + os.sep + self.screen_shot_folder_title
        img_type = '.png'

        if not os.path.exists(fq):
            os.makedirs(fq)

        tm = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        filename = fq + os.sep + tm + '{}.png'.format(name)
        time.sleep(wait_time if wait_time else self.screen_shot_wait_time)
        self.driver.get_screenshot_as_file(filename)
        return filename

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
