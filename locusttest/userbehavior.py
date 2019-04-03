import time
from functools import wraps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

from locust import events


def locust_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            request_type = kwargs.get('request_type')
            name = kwargs.get('name')
            result = func(*args, **kwargs)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type=request_type, name=name, response_time=total_time,
                                        exception=e)
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type=request_type, name=name, response_time=total_time,
                                        response_length=0)

            return result

    return wrapper


class UserBehavior(object):
    def __init__(self, host=None, browser=None):
        self.host = host
        self.browser = browser

    def open_browser(self):
        """
        默认使用Chrome浏览器
        :return:
        """
        if self.browser is None:
            self.browser = webdriver.Chrome()

    def set_window_size(self, width, height, *args, **kwargs):
        self.browser.set_window_size(width, height)

    @locust_decorator
    def get(self, url, *args, **kwargs):
        """
        模拟浏览器访问url
        :param url:
        :return:
        """
        if self.browser is None:
            self.open_browser()

        self.browser.get(url)

    def open_window_handle(self, url="", *args, **kwargs):
        self.browser.execute_script('window.open("%s");' % url)
        return self.get_window_handles()[-1]

    @locust_decorator
    def execute_script(self, script, *args, **kwargs):
        self.browser.execute_script(script)

    def get_current_window_handle(self, *args, **kwargs):
        return self.browser.current_window_handle

    def get_window_handles(self, *args, **kwargs):
        return self.browser.window_handles

    def get_current_url(self, *args, **kwargs):
        return self.browser.current_url()

    def switch_to_window(self, handle, *args, **kwargs):
        self.browser.switch_to_window(handle)

    def maximize_window(self, *args, **kwargs):
        self.browser.maximize_window()

    @locust_decorator
    def refresh(self, *args, **kwargs):
        self.browser.refresh()

    def wait_until(self, timeout, by_strategies, by_strategies_name):
        return WebDriverWait(self.browser, timeout).until(
            expected_conditions.presence_of_element_located((by_strategies, by_strategies_name)))

    def find_element(self, by_id=None, by_xpath=None, by_link_text=None, by_partial_link_text=None, by_name=None,
                     tag_name=None, by_class_name=None, by_css_selector=None,
                     timeout=None, *args, **kwargs):
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

    @locust_decorator
    def click(self, *args, **kwargs):
        self.find_element(*args, **kwargs).click()

    @locust_decorator
    def double_click(self, *args, **kwargs):
        ActionChains(self.browser).double_click(self.find_element(*args, **kwargs)).perform()

    def move_to_element(self, *args, **kwargs):
        ActionChains(self.browser).move_to_element(self.find_element(*args, **kwargs)).perform()

    @locust_decorator
    def send_keys(self, value, *args, **kwargs):
        self.find_element(*args, **kwargs).send_keys(value)

    @locust_decorator
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

    def run_func_by_name(self, func_name, *args, **kwargs):
        func = getattr(self, func_name)
        return func(*args, **kwargs)
