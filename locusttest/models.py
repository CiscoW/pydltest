from django.db import models
from basedata import get_uuid


# Create your models here.

class LocustTest(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False, db_column='id')
    test_data = models.TextField('Json数据', db_column='test_data')

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'locust_test'
        verbose_name_plural = verbose_name = "locust_test"


class CsvData(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False, default=get_uuid, db_column='id')
    test_id = models.CharField(max_length=32, editable=False, db_column='test_id')
    state = models.CharField(max_length=100, db_column='state')  # requests distribution
    state_data = models.TextField('Json数据', db_column='state_data')

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'csv_data'
        verbose_name_plural = verbose_name = "csv_data"


class StatisticsData(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False, db_column='id')
    data = models.TextField('Json数据', db_column='data')

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'statistics_data'
        verbose_name_plural = verbose_name = "statistics_data"
