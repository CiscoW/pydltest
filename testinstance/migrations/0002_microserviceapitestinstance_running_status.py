# Generated by Django 2.1.7 on 2019-03-27 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testinstance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='microserviceapitestinstance',
            name='running_status',
            field=models.BooleanField(db_column='running_status', default=False, verbose_name='是否在运行'),
        ),
    ]