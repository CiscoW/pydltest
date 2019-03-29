# 正常压力测试模式脚本
from locust import TaskSet, task


class Test(TaskSet):
    # [{"url": **, "method": **, "params": **, "data": **, "headers": **},
    # {"url": **, "method": **, "params": **, "data": **, "headers": **}]
    test_data = None
    api_list = None

    def on_start(self):
        self.api_list = self.test_data["api_list"]

    def on_stop(self):
        pass

    @task
    def normal_method(self):
        for api in self.api_list:
            self.client.request(**api)
