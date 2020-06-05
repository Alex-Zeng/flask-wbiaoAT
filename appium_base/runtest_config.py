from appium.webdriver.common.mobileby import MobileBy
import os
from appium_base import PATH


class RuntestConfig():
    use_output_arg_symbol = '$$'
    find_ele_wait_time = 10
    take_screen_shot_wait_time = 2
    find_ele_types = {'xpath': MobileBy.XPATH, 'id': MobileBy.ID, 'css': MobileBy.CSS_SELECTOR,
                      'class': MobileBy.CLASS_NAME,
                      'tag': MobileBy.TAG_NAME, 'android_uiautomator': MobileBy.ANDROID_UIAUTOMATOR,
                      'accessibility_id': MobileBy.ACCESSIBILITY_ID, 'tap_by_proportional': '按屏幕千分比点击坐标',
                      'tap_by_coordinates': '点击坐标', 'ios_predicate': MobileBy.IOS_PREDICATE,
                      'ios_class_chain': MobileBy.IOS_CLASS_CHAIN, 'ios_uiautomation': MobileBy.IOS_UIAUTOMATION, }
    screenShotsDir = PATH('screen_shot')
    pageSourceDir = PATH('pageSourceDir')
    logDir = PATH('logs')
    func_dict = {
        '点击': 'click',
        '清除文本': 'clear_text',
        '输入文本': 'input_text',
        '获取元素文本': 'get_element_text',
        '断言元素': 'check_element',
        '断言元素列表': 'check_elements',
        '断言当前页面': 'check_activity',
        '获取页面源文件': 'get_page_source',
        '后退': 'back',
        '屏幕上滑': 'swipe_to_up',
        '屏幕下滑': 'swipe_to_down',
        '屏幕左滑': 'swipe_to_left',
        '屏幕右滑': 'swipe_to_right',
        '长按元素': 'long_press',
        '点击坐标': 'tap_by_coordinates',
        '按比例点击坐标': 'tap_by_proportional',
        '回车': 'press_enter',
        '执行adb命令': 'execute_adb_cmd',
        '查找元素': 'find_element',
        '查找元素们': 'find_elements',
        '切换到native': 'switch_to_native_app',
        '切换到webview': 'switch_to_webview',
        '获取contexts': 'get_contexts',
        '获取当前context': 'get_current_context',
        '等待': 'wait',
        '关闭浮窗广告': 'if_dialog_close',
        '遍历元素': 'travel_elements',
        '深度遍历元素': 'travel_elements_more',
        '截图': 'take_screen_shot',
        '断言文本存在': 'check_text',
        '移动元素到左上角': 'move_away_el',
        '切换window_handle': 'switch_window_handle',
    }


rtconf = RuntestConfig()

if __name__ == '__main__':
    print(rtconf.screenShotsDir)
