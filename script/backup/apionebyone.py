# 一个一个接口进行压力测试
import time
from locust import TaskSet, task


class Test(TaskSet):
    # [{"url": **, "method": **, "params": **, "data": **, "headers": **},
    # {"url": **, "method": **, "params": **, "data": **, "headers": **}]

    test_data = None
    api_list = None
    run_time = None  # 用户运行时间秒

    api_list_num = None

    start_time = int(time.time())

    def on_start(self):
        self.api_list = self.test_data["api_list"]
        self.run_time = self.test_data["run_time"]
        self.api_list_num = len(self.api_list)

    def on_stop(self):
        pass

    @task
    def one_by_one_method(self):
        import time
        import random
        import gevent
        _lock = gevent.lock.Semaphore()
        for api in self.api_list:
            _lock.acquire()
            go_on = True
            start_time = int(time.time())
            while go_on:
                self.client.request(**api)
                sleep_time = random.randint(self.min_wait, self.max_wait)
                time.sleep(sleep_time / 1000)
                if int(time.time()) - start_time >= self.run_time / self.api_list_num:
                    go_on = False
            _lock.release()
