from django.conf.urls import url
from locusttest.views import *

urlpatterns = [

    url(r'testData/(\w{10,40})/$', get_test_data),
    url(r'csvData/(?P<test_id>\w+)/(?P<state>\w+)/$', get_csv_data),
    url(r'StatisticsData/(?P<test_id>\w+)/$', get_statistics_data),
    url(r'saveCsvData/$', save_csv_data),
    url(r'saveStatisticsData/$', save_statistics_data),
    url(r'updateRunningStatus/?(?P<test_id>\w{0,40})/$', update_running_status),

]
