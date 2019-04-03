from django.contrib import admin
from testcontent.models import *


# Register your models here.

@admin.register(MicroServiceApi)
class MicroServiceApiAdmin(admin.ModelAdmin):
    list_display = ['url', 'request_method', 'service_source', 'params', 'body', 'describe']
    fields = (('url', 'request_method', 'service_source'), ('params', 'body'), 'describe')
    search_fields = ('url', 'service_source')

    list_filter = ('service_source', 'request_method')
