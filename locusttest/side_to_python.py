# Selenium IDE JSON 数据对应 Selenium Python 规则

import json
from locusttest.userbehavior import UserBehavior

COMMAND_DIC = {
    'open': 'get',
    'type': 'send_keys',
    'click': 'click',
    'setWindowSize': 'set_window_size',
    'select': 'select',
    'addSelection': 'select',
    'doubleClick': 'double_click',
}

TARGET_DIC = {
    'id': 'by_id',
    'css': 'by_css_selector',
    'linkText': 'by_link_text',
    'xpath': 'by_xpath',
    'name': 'by_name',
}

# target中不是用于查找元素的command集合
NON_ELEMENT = {"open", "setWindowSize", ""}


class LazyProperty(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


class Side(object):
    def __init__(self, file):
        # pyside = None
        json_data = open(file, encoding='utf-8')
        self.side_data = json.load(json_data)

    @property
    def url(self):
        return self.side_data['url']

    @property
    def tests(self):
        return self.side_data['tests']

    @staticmethod
    def commands(test):
        return test['commands']

    # 用于判断是否有command/target没有建立对应关系
    @LazyProperty
    def command_target_set(self):
        command_set = set()
        target_set = set()
        for test in self.tests:
            for item in self.commands(test):
                command = item['command']
                target = item['target']
                command_set.add(command)
                if command not in NON_ELEMENT and '=' in target:
                    target_set.add(target.split('=', 1)[0])

        command_target_set = {'command': command_set, 'target': target_set}
        return command_target_set

    @property
    def command_set(self):
        return self.command_target_set['command']

    @property
    def target_set(self):
        return self.command_target_set['target']

    def check_command(self):
        return self.command_set - set(COMMAND_DIC.keys())

    def check_target(self):
        return self.target_set - set(TARGET_DIC.keys())

    @staticmethod
    def command_to_python(command):
        return COMMAND_DIC[command]

    def target_to_python(self, command, target):
        target_to_python = {}
        if command == 'setWindowSize':
            window_size = target.split('x')
            target_to_python['width'] = window_size[0]
            target_to_python['height'] = window_size[1]

        elif command == 'open':
            target_to_python['url'] = self.url + target

        return target_to_python


if __name__ == '__main__':
    # user_behavior = UserBehavior()
    # user_behavior.get("http://localhost:8000")
    # user_behavior.run_fuc_by_name("set_window_size", 1920, 1050)
    # user_behavior.run_fuc_by_name("send_keys", "admin", by_id="id_username")
    # user_behavior.run_fuc_by_name("send_keys", "admin", by_id="id_password")
    # user_behavior.run_fuc_by_name("click", by_css_selector=".submit-row > input")
    # user_behavior.run_fuc_by_name("click", by_link_text="微服务接口压力测试实例")
    # user_behavior.run_fuc_by_name("click", by_link_text="增加 微服务接口压力测试实例")
    # user_behavior.run_fuc_by_name("click", by_link_text="今天")
    # user_behavior.run_fuc_by_name("click", by_id="id_test_mode")
    # user_behavior.run_fuc_by_name("select", by_visible_text="正常模式", by_id="id_test_mode")
    # user_behavior.run_fuc_by_name("click", by_id="id_test_mode")
    # user_behavior.run_fuc_by_name("click", by_id="id_host")
    # user_behavior.run_fuc_by_name("send_keys", "http://localhost:5000", by_id="id_host")
    #
    # user_behavior.run_fuc_by_name("select", by_visible_text="/test2 test", by_id="id_test_content_from")
    # user_behavior.run_fuc_by_name("click", by_css_selector="#id_test_content_from > option:nth-child(1)")
    # user_behavior.run_fuc_by_name("click", by_css_selector="#id_test_content_from > option:nth-child(1)")
    #
    # user_behavior.run_fuc_by_name("double_click", by_css_selector="#id_test_content_from > option:nth-child(1)")
    #
    # user_behavior.run_fuc_by_name("select", by_visible_text="/test1 test", by_id="id_test_content_from")
    # user_behavior.run_fuc_by_name("click", by_css_selector="option:nth-child(5)")
    # user_behavior.run_fuc_by_name("click", by_id="id_test_content_add_link")
    side = Side("../script/dltest.side")
    print(side.url)
    print(side.command_set)
    print(side.command_set)
    print(side.target_set)
    print(side.check_command())
    print(side.check_target())
    print(side.target_to_python("open", "/"))
