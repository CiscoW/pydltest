import importlib

from locust import HttpLocust
from locusttest.seleniumlocust import SeleniumLocustBounded
from locusttest.seleniumlocust import SeleniumLocustUnbounded


def decorator(test_data):
    test_type = test_data["test_type"]
    browser_mode = test_data["browser_mode"]
    import_path = test_data["import_path"]
    test_mode = importlib.import_module(import_path)
    test_task = test_mode.Test
    # 将test_data传入到test_task脚本中通用性更好
    test_task.test_data = test_data
    if test_type == "api":
        class WebsiteUser(HttpLocust):
            task_set = test_task
            host = test_data["host"]
            min_wait = test_data["min_wait"]
            max_wait = test_data["max_wait"]
    elif test_type == "browser":
        if browser_mode == "有界":
            class WebsiteUser(SeleniumLocustBounded):
                task_set = test_task
                host = test_data["host"]
                min_wait = test_data["min_wait"]
                max_wait = test_data["max_wait"]
        elif browser_mode == "无界":
            class WebsiteUser(SeleniumLocustUnbounded):
                task_set = test_task
                host = test_data["host"]
                min_wait = test_data["min_wait"]
                max_wait = test_data["max_wait"]

    return WebsiteUser
