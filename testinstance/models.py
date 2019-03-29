from django.db import models
from basedata import get_uuid
from basedata.models import PressureTestMode
from testcontent.models import MicroServiceApi


# Create your models here.
class MicroServiceApiTestInstance(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False, default=get_uuid, db_column='id')
    test_date = models.DateField('日期')
    test_mode = models.ForeignKey(PressureTestMode, verbose_name='测试方式', on_delete=models.PROTECT,
                                  db_column='test_mode')
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

    def __str__(self):
        return "微服务接口压力测试实例"

    class Meta:
        db_table = 'micro_service_api_test_instance'
        verbose_name_plural = verbose_name = "微服务接口压力测试实例"
