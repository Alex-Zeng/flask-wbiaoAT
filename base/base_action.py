#!/usr/bin/python3
# @Time    : 2019/6/28 14:08
# @Author  : 曾德辉
# @File    : base_action.py
from appium.webdriver.common.mobileby import MobileBy
from base import rtconf
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.wait import WebDriverWait
import time
import os
import re
import traceback


PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


class BaseAction:

    def __init__(self, driver, log, thread_name):
        self.driver = driver
        self._by_type = rtconf.find_ele_types
        self.current_case = dict()
        self.log = log
        self.thread_name = thread_name
        self.ele_wait_time = rtconf.find_ele_wait_time
        self.screen_shot_wait_time = rtconf.take_screen_shot_wait_time
        self.case_title = ''

    def action(self, case_list, data):
        """
        循环执行用例集中每条用例对应的action方法
        :param case_list: 经过清洗组合用例列表
        :param data: 用例数据列表
        :return:
        """
        test_data = data
        for v in case_list:
            self.current_case = v
            case_id = v['id']
            wait_time = v['wait_time']
            action_title = v['action_title']
            action = v['action']
            find_type = v['type']
            screenshot = v['screen_shot']
            element_info = v['element_info']
            element_loc = v['element_loc']
            input_data = v['input_arg']
            output_data = v['output_arg']
            text = ''
            self.log.info('执行用例{}:{}'.format(case_id, action_title))
            loc = self._by_type.get(find_type, MobileBy.XPATH), element_loc

            # 是否引用前面某个用例的 输出值
            if input_data.startwith(rtconf.use_output_arg_symbol):
                input_data = test_data[input_data[len(rtconf.use_output_arg_symbol):]]

            try:
                output_text = self.__getattribute__(action)(loc,input_data)
                if output_data == 'verify_code':
                    # 测试环境验证码,只匹配数字
                    pattern = re.compile('\d{6}')
                    output_text = pattern.search(output_text).group()
                    # 输处返回参数，给依赖用例使用
                    test_data[output_data] = output_text
                else:
                    test_data[output_data] = output_text

                self.log('{}: {} --- {} --- {}'.format(case_id, action_title, element_info, '成功'))

            except Exception as e:
                self.log('错误: {} --- {} --- {}'.format(action_title, element_info, loc),
                              '用例id:{} --- 失败!!!!!'.format(case_id))
                self.log.error(v)
                self.log.error(traceback.format_exc())
                raise e
            finally:
                # 截图
                if screenshot:
                    time.sleep(wait_time)
                    self.take_screen_shot()

    def click(self, *args):
        """
        点击
        """
        self.find_element(args[0]).click()

    def clear_text(self, *args):
        """
        清除文本
        """
        self.find_element(args[0]).clear()

    def input_text(self, *args):
        """
        输入文本
        """
        self.find_element(args[0]).send_keys(args[1])

    def get_element_text(self, *args):
        """
        获取元素文本
        """
        return self.find_element(args[0]).get_attribute("text")

    def check_element(self, *args):
        """
        断言元素是否存在
        """
        try:
            assert self.find_element(args[0])
            f = self.driver.get_screenshot_as_png()
            self.log.info('成功找到{}元素，截图保留'.format(args[0]))
            self.log.info('断言成功')
        except Exception as e:
            self.log.error('断言失败未找到元素{}'.format(args[0]))
            f = self.driver.get_screenshot_as_png()
            self.log.info('未找到{}元素，截图保留'.format(args[0]))
            raise e

    def check_text(self, *args):
        """
         判断文本是否相等
        """
        assert args[1] in self.find_element(args[0]).get_attribute("text")
        self.log.info('断言成功:文本{} 存在'.format(args[1]))

    def check_elements(self, *args):
        """
        断言元素（多个）是否存在
        """
        try:
            assert self.find_elements(args[0])
            f = self.driver.get_screenshot_as_png()
            self.log.info('成功找到{}元素，截图保留'.format(args[0]))
            self.log.info('断言成功')
        except Exception as e:
            self.log.error('断言失败未找到元素{}'.format(args[0]))
            f = self.driver.get_screenshot_as_png()
            self.log.info('未找到{}元素，截图保留'.format(args[0]))
            raise e

    def check_activity(self, *args):
        """
        检查是否activity是否符合预期
        """
        expect_activity = args[1]
        cur_activity = self.driver.current_activity
        try:
            assert cur_activity == expect_activity
            f = self.driver.get_screenshot_as_png()
            self.log.info('预期页面，截图保留'.format(args[0]))
            self.log.info('是预期页面')
            return 'current_activity: {}, -- expect_activity: {}'.format(cur_activity, expect_activity)
        except Exception as e:
            self.log.error('断言失败:非预期页面{}'.format(expect_activity))
            f = self.driver.get_screenshot_as_png()
            self.log.info('非预期页面，截图保留'.format(args[0]))
            raise e

    def get_page_source(self, *args):
        """
        得到当前页面源文件
        """
        self.conf.get_filepath('pageSourceDir')
        case_path = self.conf.get_filepath('pageSourceDir') + os.sep + self.driver.current_activity + '.xml'

        if not os.path.exists(case_path):
            f = open(case_path, 'w', encoding='utf-8')
            f.write(self.driver.page_source)
            f.close()

    def back(self, *args):
        """
        后退
        """
        self.driver.back()

    def move_away_el(self,*args):
        """
        移开某个元素，防止遮挡
        :return:
        """
        try:
            el = self.find_element(args[0])
            end_x = el.size.get('x')
            end_y = el.size.get('y')
            touch_action = TouchAction(self.driver)
            touch_action.long_press(el).move_to(x=end_x, y=end_y).release().perform()
        except:
            self.log.info('没有这个元素')


    def over(self, *args):
        """
        退出
        """
        self.driver.quit()

    def get_size(self, *args):
        """
        获取界面大小
        """
        x = self.driver.get_window_size()['width']
        y = self.driver.get_window_size()['height']
        return x, y

    def if_dialog_close(self, *args):
        """
        关闭浮窗广告
        """
        try:
            self.find_element(args[0]).click()
        except:
            self.log.info("没有浮窗广告")
            return "没有浮窗广告"

    def wait(self, *args):
        """
        等待几秒(传整数参数))
        """
        s = 3  # 默认三秒

        time.sleep(s if not args[1] else args[1])

    def get_contexts(self, *args):
        """
        获取contexts
        """
        contexts = self.driver.contexts
        self.log.info(contexts)
        return contexts

    def get_current_context(self, *args):
        """
        获取当前context
        """
        context = self.driver.context
        self.log.info(context)
        return context

    def switch_to_webview(self, *args):
        """
        切换到webview或者最后一个webview
        """
        contexts = self.get_contexts()
        if args[1] and args[1] in contexts:
            self.driver.switch_to.context(args[1])
        else:
            self.driver.switch_to.context(contexts[-1])

    def get_current_window_handle(self, *args):
        """
        获取当前window_handle
        :param args:
        :return:
        """
        return self.driver.current_window_handle

    def switch_window_handle(self, *args):
        """
        切换window_handles或者最后一个handle
        """
        window_handles = self.driver.window_handles()
        if args[1] and args[1] in window_handles:
            self.driver.switch_to.window(args[1])
        else:
            self.driver.switch_to.window(window_handles[-1])


    def switch_to_native_app(self, *args):
        """
        切换到native
        """
        self.driver.switch_to.context('NATIVE_APP')

    def swipe_to_up(self, *args):
        """
        向上滑动屏幕
        """
        screen_size = self.get_size()
        x1 = int(screen_size[0] * 0.5)

        # %60的距离,相当于滑动一页
        y1 = int(screen_size[1] * 0.7)
        y2 = int(screen_size[1] * 0.1)
        self.driver.swipe(x1, y1, x1, y2, 1000)

    def swipe_to_down(self, *args):
        """
        向下滑动屏幕
        """
        screen_size = self.get_size()
        x1 = int(screen_size[0] * 0.5)
        # %50的距离,相当于滑动一页
        y1 = int(screen_size[1] * 0.3)
        y2 = int(screen_size[1] * 0.9)
        self.driver.swipe(x1, y1, x1, y2, 1000)

    def swipe_to_right(self, *args):
        """
        向右滑动屏幕
        """
        screen_size = self.get_size()
        x1 = int(screen_size[0] * 0.2)
        y1 = int(screen_size[1] * 0.5)
        x2 = int(screen_size[1] * 0.8)
        self.driver.swipe(x1, y1, x2, y1, 1000)

    def swipe_to_left(self, *args):
        """
        向左滑动屏幕
        """
        screen_size = self.get_size()
        x1 = int(screen_size[0] * 0.8)
        y1 = int(screen_size[1] * 0.5)
        x2 = int(screen_size[1] * 0.2)
        self.driver.swipe(x1, y1, x2, y1, 1000)

    def long_press(self, *args):
        """
        长按元素
        """
        ele = self.find_element(args[0])
        TouchAction(self.driver).long_press(ele).perform()

    def tap_by_coordinates(self, *args):
        """
        点击坐标
        """
        x, y = args[1].split('|')
        TouchAction(self.driver).tap(x=x, y=y).perform()

    def tap_by_proportional(self, *args):
        """
        按屏幕比例点击坐标
        """
        x, y = args[1].split('|')
        width, height = self.get_size()
        x = int(float(x) * width)
        y = int(float(y) * height)
        TouchAction(self.driver).tap(x=x, y=y).perform()

    def refresh(self, *args):
        """
        刷新
        """
        self.driver.refresh()

    def press_enter(self, *args):
        """
        按下回车键
        """
        self.driver.keyevent(66)

    def execute_adb_cmd(self, *args):
        """
        执行adb命令
        """
        os.system(args[1])

    def find_element(self, loc):
        """
        查找符合的元素并返回
        return: 元素对象
        """
        by = loc[0]
        value = loc[1]
        if by == MobileBy.XPATH:
            value = self.make_xpath_with_feature(value)
        return WebDriverWait(self.driver, self.ele_wait_time, 1).until(lambda x: x.find_element(by, value))

    def find_elements(self, loc):
        """
        查找所有符合预期的元素元素
        return: 元素对象列表
        """
        by = loc[0]
        value = loc[1]
        if by == MobileBy.XPATH:
            value = self.make_xpath_with_feature(value)
        return WebDriverWait(self.driver, self.ele_wait_time, 1).until(lambda x: x.find_elements(by, value))

    def to_activity(self, *args):
        """
        启动activity
        :param args:
        :return:
        """
        app_package = self.driver.desired_capabilities().get('appPackage')
        self.driver.start_activity(app_package, args[1])

    def travel_elements(self, *args):
        """
        遍历元素,点击,返回两个操作
        """
        elements = self.find_elements(args[0])
        before_click_activity = self.driver.current_activity
        for i in range(len(elements)):
            self.find_elements(args[0])[i].click()
            time.sleep(1)
            pagename = "元素{}点击后".format(i)
            self.take_screen_shot(name=pagename)
            if before_click_activity != self.driver.current_activity:
                self.back()

    def travel_elements_digui(self, locs, k=0):
        """
        递归遍历元素,点击,返回两个操作
        """
        tmp = k
        locs_len = len(locs)
        loc = MobileBy.XPATH, locs[k]
        elements = self.find_elements(loc)
        before_click_activity = self.driver.current_activity
        el_len = len(elements)
        for i in range(el_len):
            index = tmp
            self.log.info('第{}层级,长度:{},元素:{}'.format(index, el_len, i))
            self.find_elements(loc)[i].click()

            self.take_screen_shot(name='层级{}-第{}个元素'.format(index, i))
            while index < locs_len - 1:
                index += 1
                self.travel_elements_digui(locs=locs, k=index)

            after_click_activity = self.driver.current_activity
            while before_click_activity != after_click_activity:
                self.back()
                after_click_activity = self.driver.current_activity

    def travel_elements_more(self, *args):
        """
        纵向遍历元素,点击,返回两个操作
        """
        locs = args[1].split("|")
        self.travel_elements_digui(locs)

    def take_screen_shot(self, *args, name='截图',wait_time=None):
        """
        method explain:获取当前屏幕的截图
        parameter explain：【name】 截图的名称
        Usage:
            device.take_screenShot(u"个人主页")   #实际截图保存的结果为：2018-01-13_17_10_58_个人主页.png
        """
        day = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        tm = time.strftime("%H_%M_%S", time.localtime(time.time()))
        fq = rtconf.screenShotsDir + os.sep + day + os.sep + self.thread_name + '_' + self.case_title
        img_type = '.png'

        if os.path.exists(fq):
            filename = fq + os.sep + tm + "_" + self.current_case.get(
                'step', 'action') + name + img_type
        else:
            os.makedirs(fq)
            filename = fq + os.sep + tm + "_" + self.current_case.get(
                'step', 'action') + name + img_type
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
            if loc.startswith("//"):
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