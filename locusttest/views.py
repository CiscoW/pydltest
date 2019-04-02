import json

# from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from locusttest.models import *
from testinstance.models import MicroServiceApiTestInstance
from testinstance.models import SeleniumTestInstance


# Create your views here.
# @login_required(login_url='/login/')
def get_test_data(request, test_id):
    test_data = LocustTest.objects.values('test_data').filter(id=test_id)[0]["test_data"]

    return HttpResponse(test_data, content_type="application/json")


def get_csv_data(request, test_id, state):
    state_data = CsvData.objects.values('state_data').filter(test_id=test_id, state=state)
    if state_data:
        state_data = state_data[0]["state_data"]
    else:
        state_data = []

    return HttpResponse(state_data, content_type="application/json")


def get_statistics_data(request, test_id):
    statistics_data = StatisticsData.objects.values('data').filter(id=test_id)
    if statistics_data:
        statistics_data = statistics_data[0]["data"]
    else:
        statistics_data = json.dumps({})

    return HttpResponse(statistics_data, content_type="application/json")


@csrf_exempt
def save_csv_data(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        test_id = received_json_data["test_id"]
        state = received_json_data["state"]
        state_data = json.dumps(received_json_data["state_data"])
        if CsvData.objects.filter(test_id=test_id, state=state):
            CsvData.objects.filter(test_id=test_id, state=state).update(state_data=state_data)
        else:
            CsvData.objects.create(test_id=test_id, state=state, state_data=state_data)

        return HttpResponse(json.dumps({"state": "success"}))

    else:
        return HttpResponse('It is not a POST request !')


@csrf_exempt
def save_statistics_data(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        test_id = received_json_data["test_id"]
        statistics_data = json.dumps(received_json_data["statistics_data"])
        if StatisticsData.objects.filter(id=test_id):
            StatisticsData.objects.filter(id=test_id).update(data=statistics_data)
        else:
            StatisticsData.objects.create(id=test_id, data=statistics_data)

        return HttpResponse(json.dumps({"state": "success"}))

    else:
        return HttpResponse('It is not a POST request !')


def update_running_status(request, test_id):
    if test_id:
        # running_status = MicroServiceApiTestInstance.objects.values('running_status').filter(id=test_id)[0][
        #     "running_status"]
        running_status_query_set = MicroServiceApiTestInstance.objects.values('running_status').filter(id=test_id)
        if running_status_query_set:
            running_status = running_status_query_set[0]["running_status"]
            if running_status:
                MicroServiceApiTestInstance.objects.filter(id=test_id).update(running_status=False)
            else:
                MicroServiceApiTestInstance.objects.filter(id=test_id).update(running_status=True)
        else:
            running_status_query_set = SeleniumTestInstance.objects.values('running_status').filter(id=test_id)
            if running_status_query_set:
                running_status = running_status_query_set[0]["running_status"]
                if running_status:
                    SeleniumTestInstance.objects.filter(id=test_id).update(running_status=False)
                else:
                    SeleniumTestInstance.objects.filter(id=test_id).update(running_status=True)

    else:
        MicroServiceApiTestInstance.objects.filter(running_status=True).update(running_status=False)
        SeleniumTestInstance.objects.filter(running_status=True).update(running_status=False)

    return HttpResponse(json.dumps({"state": "success"}))
