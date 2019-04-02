# Generated by Django 2.1.7 on 2019-04-02 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testinstance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='seleniumtestinstance',
            name='describe',
            field=models.TextField(blank=True, db_column='describe', null=True, verbose_name='描述'),
        ),
        migrations.AddField(
            model_name='seleniumtestinstance',
            name='running_status',
            field=models.BooleanField(db_column='running_status', default=False, verbose_name='是否在运行'),
        ),
    ]