# flask
PORT = "8089"
URL = "http://localhost:" + PORT

RECEIVE_TEST_DATA_URL = URL + "/locust_data"
GET_LOCUST_SERVICE_STATE_URL = URL + "/getLocustServiceState/%s"
INDEX_URL = URL + "/%s"

# django
DJANGO_GET_TEST_DATA_URL = "http://localhost:8000" + "/locust/testData/%s/"
DJANGO_GET_CSV_DATA_URL = "http://localhost:8000" + "/locust/csvData/%s/%s/"
DJANGO_GET_STATISTICS_DATA_URL = "http://localhost:8000" + "/locust/StatisticsData/%s/"
DJANGO_GET_UPDATE_RUNNING_STATUS_URL = "http://localhost:8000" + "/locust/updateRunningStatus/"

DJANGO_POST_CSV_DATA_URL = "http://localhost:8000" + "/locust/saveCsvData/"
DJANGO_POST_STATISTICS_DATA_URL = "http://localhost:8000" + "/locust/saveStatisticsData/"
