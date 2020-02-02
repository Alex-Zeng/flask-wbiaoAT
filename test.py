from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
desired_caps = {
  "platformName": "iOS",
  "deviceName": "Iphone6",
  "platformVersion": "13.3",
  "automationName": "XCUITest",
  "bundleId": "com.wbiao.newwbiao",
  "udid": "3b28acdc016a68bfd90df617d62bf138ec34c459"
}

driver = webdriver.Remote('http://192.168.137.167:4723/wd/hub', desired_caps)
print(driver.page_source)
driver.find_element(MobileBy.XPATH, '//XCUIElementTypeButton[@name="我的"]').click()
driver.back()
driver.find_element(MobileBy.XPATH, '//XCUIElementTypeButton[@name="我的"]').click()