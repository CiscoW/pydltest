from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("https://blog.csdn.net/v_JULY_v/article/details/40984699")
driver.execute_script("window.scrollTo(0,100)")
driver.find_element_by_class_name(name="").send_keys()
