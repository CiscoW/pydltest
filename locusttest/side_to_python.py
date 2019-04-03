# Selenium IDE JSON 数据对应 Selenium Python 规则

import json
import copy

COMMAND_DIC = {
    'open': 'get',
    'type': 'send_keys',
    'click': 'click',
    'setWindowSize': 'set_window_size',
    'select': 'select',
    'addSelection': 'select',
    'doubleClick': 'double_click',
    'runScript': 'execute_script',
    'mouseDown': 'move_to_element',
    'mouseDownAt': 'move_to_element',
    'mouseUp': 'move_to_element',
    'mouseUpAt': 'move_to_element',
    'mouseMoveAt': 'move_to_element',
    'mouseOver': 'move_to_element',
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
    def __init__(self, file=None, side_data=None):
        if file:
            json_data = open(file, encoding='utf-8')
            self.side_data = json.load(json_data)
        else:
            self.side_data = json.loads(side_data)

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
        command_to_python = {'func_name': COMMAND_DIC[command]}
        return command_to_python

    def target_to_python(self, command, target):
        target_to_python = {}
        if command == 'setWindowSize':
            window_size = target.split('x')
            target_to_python['width'] = window_size[0]
            target_to_python['height'] = window_size[1]

        elif command == 'open':
            target_to_python['url'] = self.url + target

        elif command == 'runScript':
            target_to_python['script'] = target

        else:
            element = target.split('=', 1)
            # 转换成Python kwargs
            target_to_python[TARGET_DIC[element[0]]] = element[1]

        return target_to_python

    @staticmethod
    def value_to_python(command, value):
        value_to_python = {}
        if command == 'select' or command == 'addSelection':
            value = value.split('=', 1)[1]
            value_to_python['by_visible_text'] = value
        else:
            value_to_python['value'] = value

        return value_to_python

    @LazyProperty
    def pyside(self):
        pyside = copy.deepcopy(self.side_data)
        for test in pyside['tests']:
            for item in test['commands']:
                command = item['command']
                target = item['target']
                value = item['value']
                command_python = self.command_to_python(command)
                target_python = self.target_to_python(command, target)
                value_python = self.value_to_python(command, value)
                # 用于压力测试展示的
                request_type = {'request_type': command}
                name = {'name': target}
                kwargs = dict(command_python, **target_python, **value_python, **request_type, **name)
                item['kwargs'] = kwargs

        return pyside

# if __name__ == '__main__':
#     # user_behavior = UserBehavior()
#     # user_behavior.get("http://localhost:8000")
#     # user_behavior.run_fuc_by_name("set_window_size", 1920, 1050)
#     # user_behavior.run_fuc_by_name("send_keys", "admin", by_id="id_username")
#     # user_behavior.run_fuc_by_name("send_keys", "admin", by_id="id_password")
#     # user_behavior.run_fuc_by_name("click", by_css_selector=".submit-row > input")
#     # user_behavior.run_fuc_by_name("click", by_link_text="微服务接口压力测试实例")
#     # user_behavior.run_fuc_by_name("click", by_link_text="增加 微服务接口压力测试实例")
#     # user_behavior.run_fuc_by_name("click", by_link_text="今天")
#     # user_behavior.run_fuc_by_name("click", by_id="id_test_mode")
#     # user_behavior.run_fuc_by_name("select", by_visible_text="正常模式", by_id="id_test_mode")
#     # user_behavior.run_fuc_by_name("click", by_id="id_test_mode")
#     # user_behavior.run_fuc_by_name("click", by_id="id_host")
#     # user_behavior.run_fuc_by_name("send_keys", "http://localhost:5000", by_id="id_host")
#     #
#     # user_behavior.run_fuc_by_name("select", by_visible_text="/test2 test", by_id="id_test_content_from")
#     # user_behavior.run_fuc_by_name("click", by_css_selector="#id_test_content_from > option:nth-child(1)")
#     # user_behavior.run_fuc_by_name("click", by_css_selector="#id_test_content_from > option:nth-child(1)")
#     #
#     # user_behavior.run_fuc_by_name("double_click", by_css_selector="#id_test_content_from > option:nth-child(1)")
#     #
#     # user_behavior.run_fuc_by_name("select", by_visible_text="/test1 test", by_id="id_test_content_from")
#     # user_behavior.run_fuc_by_name("click", by_css_selector="option:nth-child(5)")
#     # user_behavior.run_fuc_by_name("click", by_id="id_test_content_add_link")
#     # side = Side("../script/dl001.side")
#     from locusttest.userbehavior import UserBehavior
#
#     user_behavior = UserBehavior()
#     user_behavior.get("https://www.ithome.com/")
#     user_behavior.run_func_by_name("move_to_element", by_link_text="业界资讯")
#
#     #
#     # user_behavior = UserBehavior()
#     # print(side.pyside)
#     #
#     # for test in side.pyside["tests"]:
#     #     for item in test["commands"]:
#     #         user_behavior.run_func_by_name(**item["kwargs"])
