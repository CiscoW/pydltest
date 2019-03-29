from django.db import models
from basedata import get_uuid
from basedata.models import RequestMethod


# Create your models here.

class MicroServiceApi(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False, default=get_uuid, db_column='id')
    url = models.CharField('服务(url)', max_length=200, db_column='url')
    request_method = models.ForeignKey(RequestMethod, verbose_name='请求方法', on_delete=models.PROTECT,
                                       db_column='request_method')
    service_source = models.CharField('服务来源', max_length=100, db_column='service_source')
    params = models.TextField('请求参数', blank=True, null=True, db_column='params')
    body = models.TextField('请求体', blank=True, null=True, db_column='body')
    describe = models.TextField('描述', blank=True, null=True, db_column='describe')

    def __str__(self):
        return self.url + " " + self.service_source

    class Meta:
        db_table = 'micro_service_api'
        verbose_name_plural = verbose_name = "微服务接口明细"
