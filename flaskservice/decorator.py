import importlib

from locust import HttpLocust


def decorator(test_data):
    import_path = test_data["import_path"]
    test_mode = importlib.import_module(import_path)
    test_task = test_mode.Test
    # 将test_data传入到test_task脚本中通用性更好
    test_task.test_data = test_data

    class WebsiteUser(HttpLocust):
        task_set = test_task
        host = test_data["host"]
        min_wait = test_data["min_wait"]
        max_wait = test_data["max_wait"]

    return WebsiteUser
