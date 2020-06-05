#!/usr/bin/python3
# @Time    : 2019/6/28 14:08
# @Author  : 曾德辉
# @File    : base_driver.py

from appium import webdriver

class BaseDriver:

    def __init__(self, info_dict):
        self.desired_caps = info_dict
        self.remote_address = 'http://{host}:{port}/wd/hub'.format(host=self.desired_caps['remoteHost'],
                                                                   port=self.desired_caps['remotePort'])

    def get_driver(self):
        driver = webdriver.Remote(self.remote_address, self.desired_caps['setting_args'])
        return driver



# if __name__ == '__main__':
#     conf = Readconfig()
#     case_file, case_title = conf.get_script_info('test_welcome')
#     test_info = ReadExcel(case_file)
#     phone_info = self.test_info.get_desired_caps_and_remote_address()
#     phone_info['appActivity'] = 'com.wbiao.app.android.auction.welcome.WelcomeActivity'
#     test_data = self.test_info.get_datalist('欢迎页')
#     test_cases = self.test_info.get_case_list('欢迎页')
#     driver = BaseDriver(self.phone_info).get_driver()
#     welcome = BaseAction(self.driver)
#
#     print(driver.start_activity('com.wbiao.wbauction','com.wbiao.app.auction.MainActivity'))
#     print(driver.reset())
#
#     driver.quit()
