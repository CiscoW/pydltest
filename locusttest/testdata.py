import json
import requests
from flaskservice.config import *


def get_access_token(url, user, password, params):
    response = requests.post(url, auth=(user, password), params=params)
    access_token = json.loads(response.text)["access_token"]
    return "Bearer " + access_token


def get_api_test_data(test_instance):
    api_list = []
    test_id = test_instance.id
    host = test_instance.host
    min_wait = test_instance.min_wait
    max_wait = test_instance.max_wait
    import_path = test_instance.test_mode.import_path
    test_type = test_instance.test_mode.test_type
    locust_count = test_instance.locust_count
    hatch_rate = test_instance.hatch_rate
    run_time = test_instance.run_time

    token_url = test_instance.token_url
    if token_url:
        if "http" not in token_url and "https" not in token_url:
            token_url = host + token_url

        user = test_instance.user
        password = test_instance.password
        if test_instance.token_params:
            token_params = json.loads(test_instance.token_params)
        else:
            token_params = None
        try:
            token = get_access_token(token_url, user, password, token_params)
        except Exception as e:
            print(e)
            token = ''

        headers = {'content-type': "application/json", "Authorization": token}
    else:
        headers = {'content-type': "application/json"}

    for api in test_instance.test_content:
        url = api.url
        method = api.request_method.method
        if api.params:
            params = json.loads(api.params)
        else:
            params = None
        data = api.body
        api_list.append({"url": url, "method": method, "params": params, "data": data, "headers": headers})

    test_data = {"test_id": test_id, "host": host, "min_wait": min_wait, "max_wait": max_wait,
                 "import_path": import_path, "locust_count": locust_count, "hatch_rate": hatch_rate,
                 "run_time": run_time, "api_list": api_list, "test_type": test_type}

    # response = requests.post(RECEIVE_TEST_DATA_URL, data=json.dumps(test_data))

    return test_id, json.dumps(test_data)


def get_side_test_data(test_instance):
    test_id = test_instance.id
    host = test_instance.host
    min_wait = test_instance.min_wait
    max_wait = test_instance.max_wait
    locust_count = test_instance.locust_count
    hatch_rate = test_instance.hatch_rate
    run_time = test_instance.run_time
    import_path = test_instance.test_mode.import_path
    test_type = test_instance.test_mode.test_type
    browser_mode = test_instance.browser_mode
    time_out = test_instance.time_out
    side_path = test_instance.side.name

    test_data = {"test_id": test_id, "host": host, "min_wait": min_wait, "max_wait": max_wait,
                 "locust_count": locust_count, "hatch_rate": hatch_rate, "run_time": run_time,
                 "import_path": import_path, "browser_mode": browser_mode, "time_out": time_out, "side_path": side_path,
                 "test_type": test_type}

    return test_id, json.dumps(test_data)


def send_test_data(test_instance):
    _, test_data = get_api_test_data(test_instance)
    response = requests.post(RECEIVE_TEST_DATA_URL, data=test_data)
    return response
