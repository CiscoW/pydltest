from selenium import webdriver

driver = webdriver.Chrome()
driver.set_window_size()
driver.get("https://www.baidu.com/")
el = driver.find_element_by_id("kw")
el.click()
driver.find_element_by_class_name()
el.send_keys("测试")
