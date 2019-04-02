from locust import Locust
from locusttest.userbehavior import UserBehavior
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class SeleniumLocustBounded(Locust):
    """
    扩展locust的能力
    """

    def __init__(self, *args, **kwargs):
        super(SeleniumLocustBounded, self).__init__(*args, **kwargs)
        self.client = UserBehavior(self.host)


class SeleniumLocustUnbounded(Locust):
    """
    扩展locust的能力
    """

    def __init__(self, *args, **kwargs):
        super(SeleniumLocustUnbounded, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.client = UserBehavior(host=self.host, browser=webdriver.Chrome(options=chrome_options))
