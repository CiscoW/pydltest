from django.db import models
from basedata import get_uuid


def upload_path(instance, filename):
    upload_dir = 'script/' + filename
    return upload_dir


TEST_TYPE = (
    ("api", "api"),
    ("browser", "browser"),
    ("disable", "disable"),
)


# Create your models here.
class RequestMethod(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False, default=get_uuid, db_column='id')
    method = models.CharField('方法', max_length=10, db_column='method')
    describe = models.TextField('描述', blank=True, null=True, db_column='describe')

    def __str__(self):
        return self.method

    class Meta:
        db_table = 'request_method'
        verbose_name_plural = verbose_name = "请求方法"


class PressureTestMode(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False, default=get_uuid, db_column='id')
    test_mode = models.CharField('测试方式', max_length=100, db_column='test_mode')
    test_type = models.CharField('类别', max_length=100, choices=TEST_TYPE, db_column='test_type')
    import_path = models.CharField('测试脚本引入路径', max_length=100, unique=True, db_column='import_path')
    script = models.FileField('测试脚本文件', upload_to=upload_path, unique=True, db_column='script')
    describe = models.TextField('描述', blank=True, null=True, db_column='describe')

    def __str__(self):
        return self.test_mode

    class Meta:
        db_table = 'pressure_test_mode'
        verbose_name_plural = verbose_name = "压力测试方式"
