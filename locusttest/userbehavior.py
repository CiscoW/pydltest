import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains


class UserBehavior(object):
    def __init__(self, browser=None):
        self.browser = browser

    def open_browser(self):
        """
        默认使用Chrome浏览器
        :return:
        """
        if self.browser is None:
            self.browser = webdriver.Chrome()

    def set_window_size(self, width, height):
        self.browser.set_window_size(width, height)

    def get(self, url):
        """
        模拟浏览器访问url
        :param url:
        :return:
        """
        if self.browser is None:
            self.open_browser()

        self.browser.get(url)

    def open_window_handle(self, url=""):
        self.browser.execute_script('window.open("%s");' % url)
        return self.get_window_handles()[-1]

    def get_current_window_handle(self):
        return self.browser.current_window_handle

    def get_window_handles(self):
        return self.browser.window_handles

    def get_current_url(self):
        return self.browser.current_url()

    def switch_to_window(self, handle):
        self.browser.switch_to_window(handle)

    def maximize_window(self):
        self.browser.maximize_window()

    def refresh(self):
        self.browser.refresh()

    def wait_until(self, timeout, by_strategies, by_strategies_name):
        return WebDriverWait(self.browser, timeout).until(
            expected_conditions.presence_of_element_located((by_strategies, by_strategies_name)))

    def find_element(self, by_id=None, by_xpath=None, by_link_text=None, by_partial_link_text=None, by_name=None,
                     tag_name=None, by_class_name=None, by_css_selector=None,
                     timeout=None):
        if timeout:
            if by_id:
                return self.wait_until(timeout, By.ID, by_id)

            if by_xpath:
                return self.wait_until(timeout, By.XPATH, by_xpath)

            if by_link_text:
                return self.wait_until(timeout, By.LINK_TEXT, by_link_text)

            if by_partial_link_text:
                return self.wait_until(timeout, By.PARTIAL_LINK_TEXT, by_partial_link_text)

            if by_name:
                return self.wait_until(timeout, By.NAME, by_name)

            if tag_name:
                return self.wait_until(timeout, By.TAG_NAME, tag_name)

            if by_class_name:
                return self.wait_until(timeout, By.CLASS_NAME, by_class_name)

            if by_css_selector:
                return self.wait_until(timeout, By.CSS_SELECTOR, by_css_selector)

        else:
            if by_id:
                return self.browser.find_element_by_id(by_id)

            if by_xpath:
                return self.browser.find_element_by_xpath(by_xpath)

            if by_link_text:
                return self.browser.find_element_by_link_text(by_link_text)

            if by_partial_link_text:
                return self.browser.find_element_by_partial_link_text(by_partial_link_text)

            if by_name:
                return self.browser.find_element_by_name(by_name)

            if tag_name:
                return self.browser.find_elements_by_tag_name(tag_name)

            if by_class_name:
                return self.browser.find_element_by_class_name(by_class_name)

            if by_css_selector:
                return self.browser.find_element_by_css_selector(by_css_selector)

    def click(self, *args, **kwargs):
        self.find_element(*args, **kwargs).click()

    def double_click(self, *args, **kwargs):
        ActionChains(self.browser).double_click(self.find_element(*args, **kwargs)).perform()

    def send_keys(self, value, *args, **kwargs):
        self.find_element(*args, **kwargs).send_keys(value)

    def select(self, by_index=None, by_visible_text=None, by_value=None, *args, **kwargs):
        select = Select(self.find_element(*args, **kwargs))
        if by_index:
            select.select_by_index(by_index)

        if by_visible_text:
            select.select_by_visible_text(by_visible_text)

        if by_value:
            select.select_by_value(by_value)

    def close_current_window(self):
        self.browser.close()

    def close_browser(self):
        self.browser.quit()

    def run_fuc_by_name(self, name, *args, **kwargs):
        func = getattr(self, name)
        return func(*args, **kwargs)


if __name__ == '__main__':
    user_behavior = UserBehavior()
    # start_time_stamp = user_behavior.random_time_stamp('2018-02-20', '2019-02-26')
    # print(start_time_stamp, user_behavior.random_time_stamp(start_time_stamp, '2019-02-26'))
    user_behavior.browser_get("https://www.baidu.com")
    print(user_behavior.get_current_window_handle())
    # user_behavior.click_button(by_id="su", timeout=6)
    # user_behavior.send_keys("selenium", by_xpath='//*[@id="kw"]')
    # user_behavior.click_button(by_xpath='//*[@id="su"]', timeout=0)
    # current_handle = user_behavior.get_current_window_handle()
    # print(current_handle)
    window_handle = user_behavior.open_window_handle("https://blog.csdn.net/EB_NUM/article/details/77864470")
    print(window_handle)
    # user_behavior.browser_get("https://www.baidu.com")
    time.sleep(5)
    user_behavior.switch_to_window(window_handle)
    user_behavior.browser_get("https://www.baidu.com")
    # time.sleep(3)
    user_behavior.close_browser()
    # print(window_handle)
