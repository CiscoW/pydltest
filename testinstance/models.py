# import importlib
from django.db import models
from django.core.exceptions import ValidationError
from basedata import get_uuid
from basedata.models import PressureTestMode
from testcontent.models import MicroServiceApi


def upload_path(instance, filename):
    upload_dir = 'script/sides/' + instance.id + '/' + filename
    return upload_dir


BROWSER_MODE = (
    ('有界', '有界'),
    ('无界', '无界'),
)


# Create your models here.
class MicroServiceApiTestInstance(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False, default=get_uuid, db_column='id')
    test_date = models.DateField('日期')
    test_mode = models.ForeignKey(PressureTestMode, verbose_name='测试方式', limit_choices_to={'test_type': 'api'},
                                  on_delete=models.PROTECT, db_column='test_mode')
    host = models.CharField('host', max_length=100, db_column='host')
    min_wait = models.IntegerField('任务间最小等待时间(ms)', db_column='min_wait')
    max_wait = models.IntegerField('任务间最大等待时间(ms)', db_column='max_wait')
    run_time = models.IntegerField('模拟用户执行多长时间(s)', db_column='run_time')
    locust_count = models.IntegerField('模拟用户总数', db_column='locust_count')
    hatch_rate = models.IntegerField('每秒生成的模拟用户数', db_column='hatch_rate')
    test_content = models.ManyToManyField(MicroServiceApi, verbose_name='选取测试服务', db_column='test_content')
    token_url = models.CharField('单点登录地址', max_length=100, blank=True, null=True, db_column='token_url')
    user = models.CharField('用户', max_length=100, blank=True, null=True, db_column='user')
    password = models.CharField('密码', max_length=100, blank=True, null=True, db_column='password')
    token_params = models.TextField('参数', blank=True, null=True, db_column='token_params')

    describe = models.TextField('描述', blank=True, null=True, db_column='describe')

    running_status = models.BooleanField('是否在运行', default=False, db_column='running_status')

    def clean(self):
        if self.running_status:
            raise ValidationError('该实例正在进行压力测试, 无法修改!')

        if self.min_wait is None or self.min_wait < 0:
            raise ValidationError({'min_wait': '不能小于0'})

        if self.max_wait is None or self.max_wait < 0:
            raise ValidationError({'max_wait': '不能小于0'})

        if self.run_time is None or self.run_time < 0:
            raise ValidationError({'run_time': '不能小于0'})

        if self.locust_count is None or self.locust_count < 0:
            raise ValidationError({'locust_count': '不能小于0'})

        if self.hatch_rate is None or self.hatch_rate < 0:
            raise ValidationError({'hatch_rate': '不能小于0'})

    def __str__(self):
        return "微服务接口压力测试实例"

    class Meta:
        db_table = 'micro_service_api_test_instance'
        verbose_name_plural = verbose_name = "微服务接口压力测试实例"


class SeleniumTestInstance(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False, default=get_uuid, db_column='id')
    test_date = models.DateField('日期')
    test_mode = models.ForeignKey(PressureTestMode, verbose_name='测试方式', limit_choices_to={'test_type': 'browser'},
                                  on_delete=models.PROTECT, db_column='test_mode')
    min_wait = models.IntegerField('任务间最小等待时间(ms)', db_column='min_wait')
    max_wait = models.IntegerField('任务间最大等待时间(ms)', db_column='max_wait')
    run_time = models.IntegerField('模拟用户执行多长时间(s)', db_column='run_time')
    locust_count = models.IntegerField('模拟用户总数', db_column='locust_count')
    hatch_rate = models.IntegerField('每秒生成的模拟用户数', db_column='hatch_rate')
    browser_mode = models.CharField('是否显示浏览器', max_length=10, choices=BROWSER_MODE, db_column='browser_mode')
    time_out = models.IntegerField('查找元素超时时间(s)', db_column='time_out')
    side = models.FileField('测试脚本文件', upload_to=upload_path, unique=True, db_column='side')

    describe = models.TextField('描述', blank=True, null=True, db_column='describe')

    host = models.CharField('host', max_length=100, db_column='host')
    running_status = models.BooleanField('是否在运行', default=False, db_column='running_status')

    def clean(self):
        if self.running_status:
            raise ValidationError('该实例正在进行压力测试, 无法修改!')

        if self.min_wait is None or self.min_wait < 0:
            raise ValidationError({'min_wait': '不能为空和小于0'})

        if self.max_wait is None or self.max_wait < 0:
            raise ValidationError({'max_wait': '不能小于0'})

        if self.run_time is None or self.run_time < 0:
            raise ValidationError({'run_time': '不能小于0'})

        if self.locust_count is None or self.locust_count < 0:
            raise ValidationError({'locust_count': '不能小于0'})

        if self.hatch_rate is None or self.hatch_rate < 0:
            raise ValidationError({'hatch_rate': '不能小于0'})

        if self.time_out is None or self.time_out < 0:
            raise ValidationError({'time_out': '不能小于0'})

        if not self.side:
            raise ValidationError({'side': '请上传文件'})

        # 因为可能频繁更新所有做动态引入
        # side_to_python = importlib.import_module('locusttest.side_to_python')
        # Side = side_to_python.Side
        from locusttest.side_to_python import Side
        prompt = '上传的文件格式错误!'
        try:
            side_data = self.side.read().decode('utf-8')
            side = Side(side_data=side_data)
            self.host = side.url
            check_command = side.check_command()
            check_target = side.check_target()
            if check_command or check_target:
                prompt = '请联系系统开发人员, 更新以下内容:'
                if check_command:
                    prompt = prompt + 'command:' + str(check_command)

                if check_target:
                    prompt = prompt + 'target:' + str(check_target)

                raise ValidationError({'side': prompt})
        except Exception as e:
            raise ValidationError({'side': prompt})

    def __str__(self):
        return "模拟浏览器测试实例"

    class Meta:
        db_table = 'selenium_test_instance'
        verbose_name_plural = verbose_name = "模拟浏览器测试实例"
