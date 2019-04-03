# 正常压力测试模式脚本
import os

from locust import TaskSet, task
from locusttest.side_to_python import Side

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Test(TaskSet):
    # [{"url": **, "method": **, "params": **, "data": **, "headers": **},
    # {"url": **, "method": **, "params": **, "data": **, "headers": **}]
    test_data = None
    pyside = None
    time_out = None

    def on_start(self):
        side = Side(BASE_DIR + "/" + self.test_data["side_path"])
        self.pyside = side.pyside
        self.time_out = {"time_out": self.test_data["time_out"]}

    def on_stop(self):
        self.client.close_browser()

    @task
    def normal_method(self):
        for test in self.pyside["tests"]:
            for item in test["commands"]:
                self.client.run_func_by_name(**item["kwargs"], **self.time_out)
