class TestInstance(object):
    def __init__(self, obj):
        self.id = obj.id
        self.test_mode = TestMode(obj.test_mode)
        self.host = obj.host
        self.min_wait = obj.min_wait
        self.max_wait = obj.max_wait
        self.run_time = obj.run_time
        self.locust_count = obj.locust_count
        self.hatch_rate = obj.hatch_rate
        self.test_content = []
        self.token_url = obj.token_url
        self.user = obj.user
        self.password = obj.password
        self.token_params = obj.token_params

        for test_content in obj.test_content.all():
            self.test_content.append(TestContent(test_content))


class TestContent(object):
    def __init__(self, obj):
        self.id = obj.id
        self.url = obj.url
        self.request_method = RequestMethod(obj.request_method)
        self.service_source = obj.service_source
        self.params = obj.params
        self.body = obj.body


class RequestMethod(object):
    def __init__(self, obj):
        self.id = obj.id
        self.method = obj.method


class TestMode(object):
    def __init__(self, obj):
        self.id = obj.id
        self.test_mode = obj.test_mode
        self.import_path = obj.import_path
