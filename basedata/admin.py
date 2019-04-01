from django.contrib import admin
from basedata.models import *


# Register your models here.
@admin.register(RequestMethod)
class RequestMethodAdmin(admin.ModelAdmin):
    list_display = ['method', 'describe']


@admin.register(PressureTestMode)
class PressureTestModeAdmin(admin.ModelAdmin):
    list_display = ['test_mode', 'test_type', 'import_path', 'script', 'describe']
