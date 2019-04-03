from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://blog.csdn.net/v_JULY_v/article/details/40984699")
driver.execute_script("window.scrollTo(0,100)")
