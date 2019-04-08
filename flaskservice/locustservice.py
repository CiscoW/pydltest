import csv
import json
import os
from itertools import chain
from time import time
import urllib.request

import gevent
import six
from flask import Flask, render_template, make_response
# from flask import request
from flask import jsonify
from locust.main import parse_options, version
from locust.runners import LocalLocustRunner, MasterLocustRunner
from locust import runners
from locust.stats import sort_stats, requests_csv, distribution_csv
from six import StringIO

from flaskservice.config import *
from flaskservice.decorator import decorator

app = Flask(__name__)
app.root_path = os.path.dirname(os.path.abspath(__file__))

locust_runner_id = None
host = None


# 更新测试实例状态
def update_running_status(url, test_id=None):
    if test_id:
        get_data_from_django(url + test_id)
    else:
        get_data_from_django(url)


# 弃用
# @app.route("/locust_data", methods=["POST"])
# def locust_data():
#     test_data = json.loads(request.get_data())
#     start_pressure_test(test_data)
#
#     return jsonify({"status": "成功"})


def start_pressure_test(test_data):
    global locust_runner_id, host
    locust_runner_id = test_data["test_id"]
    host = test_data["host"]
    locust_count = test_data["locust_count"]
    hatch_rate = test_data["hatch_rate"]
    arser, options, arguments = parse_options()

    WebsiteUser = decorator(test_data=test_data)

    runners.locust_runner = LocalLocustRunner([WebsiteUser], options)
    runners.locust_runner.start_hatching(locust_count=locust_count, hatch_rate=hatch_rate)
    update_running_status(DJANGO_GET_UPDATE_RUNNING_STATUS_URL, locust_runner_id)
    gevent.spawn_later(test_data["run_time"], time_limit_stop, locust_runner_id)


# 弃用
# @app.route("/getLocustServiceState/<test_id>", methods=["GET"])
# def get_locust_service_state(test_id):
#     # test_id = json.loads(request.get_data())["test_id"]
#     if test_id == locust_runner_id:
#         return jsonify({"state": True})
#     else:
#         return jsonify({"state": False})


def get_data_from_django(url):
    # client = HttpSession(url)
    # response = client.request(method="GET", url=url)
    response = urllib.request.urlopen(url)
    return response.read().decode('utf-8')


@app.route('/<test_id>')
def index(test_id):
    is_distributed = isinstance(runners.locust_runner, MasterLocustRunner)
    if is_distributed:
        slave_count = runners.locust_runner.slave_count
    else:
        slave_count = 0

    if locust_runner_id == test_id:

        return render_template("index.html",
                               state=runners.locust_runner.state,
                               is_distributed=is_distributed,
                               user_count=runners.locust_runner.user_count,
                               version=version,
                               host=host
                               )
    else:
        test_data = json.loads(get_data_from_django(DJANGO_GET_TEST_DATA_URL % test_id))
        if test_data:
            _host = test_data['host']
        else:
            _host = '无'
        state = 'stopped'
        user_count = 0
        return render_template("index.html",
                               state=state,
                               is_distributed=is_distributed,
                               user_count=user_count,
                               version=version,
                               host=_host
                               )


def time_limit_stop(test_id):
    # 加不加锁暂时没有发现差异，并且这样加锁是否真的有多用还待观察
    _lock = gevent.lock.Semaphore()
    global locust_runner_id
    if locust_runner_id is not None and locust_runner_id == test_id:
        runners.locust_runner.quit()
        requests_csv_data = {"test_id": locust_runner_id, "state": "requests", "state_data": requests_csv()}
        distribution_csv_data = {"test_id": locust_runner_id, "state": "distribution", "state_data": distribution_csv()}
        post_data_to_django(DJANGO_POST_CSV_DATA_URL, json.dumps(requests_csv_data))
        post_data_to_django(DJANGO_POST_CSV_DATA_URL, json.dumps(distribution_csv_data))

        statistics_data = {"test_id": locust_runner_id, "statistics_data": get_statistics_data()}
        post_data_to_django(DJANGO_POST_STATISTICS_DATA_URL, json.dumps(statistics_data))
        update_running_status(DJANGO_GET_UPDATE_RUNNING_STATUS_URL, locust_runner_id)
        locust_runner_id = None
    _lock.release()


@app.route("/start/<test_id>")
def start(test_id):
    response = {'success': True, 'message': 'Test started'}
    if locust_runner_id is None:
        test_data = json.loads(get_data_from_django(DJANGO_GET_TEST_DATA_URL % test_id))
        if test_data:
            start_pressure_test(test_data)
        else:
            response['success'] = False
            response['message'] = "该实例不存在! 或已被删除!"
    else:
        response['success'] = False
        response['message'] = "启动失败! 有其他压力测试实例正在运行"
    return jsonify(response)


def post_data_to_django(url, data):
    # client = HttpSession(url)
    # response = client.request(method="POST", url=url, data=data)
    req = urllib.request.Request(url)
    req.add_header("Content-Type", "application/json;charset=utf-8")
    response = urllib.request.urlopen(req, bytes(data, 'utf-8'))
    return response.read().decode('utf-8')


def get_statistics_data():
    stats = []

    for s in chain(sort_stats(runners.locust_runner.request_stats), [runners.locust_runner.stats.total]):
        stats.append({
            "method": s.method,
            "name": s.name,
            "num_requests": s.num_requests,
            "num_failures": s.num_failures,
            "avg_response_time": s.avg_response_time,
            "min_response_time": round(s.min_response_time) if s.min_response_time else 0,
            "max_response_time": round(s.max_response_time),
            "current_rps": s.current_rps,
            "median_response_time": s.median_response_time,
            "avg_content_length": s.avg_content_length,
        })

    errors = [e.to_dict() for e in six.itervalues(runners.locust_runner.errors)]

    # Truncate the total number of stats and errors displayed since a large number of rows will cause the app
    # to render extremely slowly. Aggregate stats should be preserved.
    report = {"stats": stats[:500], "errors": errors[:500]}

    if stats:
        report["total_rps"] = stats[len(stats) - 1]["current_rps"]
        report["fail_ratio"] = runners.locust_runner.stats.total.fail_ratio
        report[
            "current_response_time_percentile_95"] = runners.locust_runner.stats.total.get_current_response_time_percentile(
            0.95)
        report[
            "current_response_time_percentile_50"] = runners.locust_runner.stats.total.get_current_response_time_percentile(
            0.5)

    is_distributed = isinstance(runners.locust_runner, MasterLocustRunner)
    if is_distributed:
        slaves = []
        for slave in runners.locust_runner.clients.values():
            slaves.append({"id": slave.id, "state": slave.state, "user_count": slave.user_count})

        report["slaves"] = slaves

    report["state"] = runners.locust_runner.state
    report["user_count"] = runners.locust_runner.user_count

    return report


@app.route("/stop/<test_id>")
def locust_stop(test_id):
    # global locust_runner_id
    # runners.locust_runner.stop()
    # requests_csv_data = {"test_id": locust_runner_id, "state": "requests", "state_data": requests_csv()}
    # distribution_csv_data = {"test_id": locust_runner_id, "state": "distribution", "state_data": distribution_csv()}
    # post_data_to_django(DJANGO_POST_CSV_DATA_URL, json.dumps(requests_csv_data))
    # post_data_to_django(DJANGO_POST_CSV_DATA_URL, json.dumps(distribution_csv_data))
    #
    # statistics_data = {"test_id": locust_runner_id, "statistics_data": get_statistics_data()}
    # post_data_to_django(DJANGO_POST_STATISTICS_DATA_URL, json.dumps(statistics_data))
    #
    # locust_runner_id = None

    time_limit_stop(test_id)

    return jsonify({'success': True, 'message': 'Test stopped'})


@app.route("/stats/reset")
def reset_stats():
    runners.locust_runner.stats.reset_all()
    return "ok"


@app.route('/stats/requests/<test_id>')
def request_stats(test_id):
    if locust_runner_id == test_id:
        stats = []

        for s in chain(sort_stats(runners.locust_runner.request_stats), [runners.locust_runner.stats.total]):
            stats.append({
                "method": s.method,
                "name": s.name,
                "num_requests": s.num_requests,
                "num_failures": s.num_failures,
                "avg_response_time": s.avg_response_time,
                "min_response_time": round(s.min_response_time) if s.min_response_time else 0,
                "max_response_time": round(s.max_response_time),
                "current_rps": s.current_rps,
                "median_response_time": s.median_response_time,
                "avg_content_length": s.avg_content_length,
            })

        errors = [e.to_dict() for e in six.itervalues(runners.locust_runner.errors)]

        # Truncate the total number of stats and errors displayed since a large number of rows will cause the app
        # to render extremely slowly. Aggregate stats should be preserved.
        report = {"stats": stats[:500], "errors": errors[:500]}

        if stats:
            report["total_rps"] = stats[len(stats) - 1]["current_rps"]
            report["fail_ratio"] = runners.locust_runner.stats.total.fail_ratio
            report[
                "current_response_time_percentile_95"] = runners.locust_runner.stats.total.get_current_response_time_percentile(
                0.95)
            report[
                "current_response_time_percentile_50"] = runners.locust_runner.stats.total.get_current_response_time_percentile(
                0.5)

        is_distributed = isinstance(runners.locust_runner, MasterLocustRunner)
        if is_distributed:
            slaves = []
            for slave in runners.locust_runner.clients.values():
                slaves.append({"id": slave.id, "state": slave.state, "user_count": slave.user_count})

            report["slaves"] = slaves

        report["state"] = runners.locust_runner.state
        report["user_count"] = runners.locust_runner.user_count
    else:
        report = json.loads(get_data_from_django(DJANGO_GET_STATISTICS_DATA_URL % test_id))

    return jsonify(report)


@app.route("/stats/requests/csv/<test_id>")
def request_stats_csv(test_id):
    # 加上BOM头解决中文乱码问题
    BOM = '\uFEFF'
    if locust_runner_id == test_id:
        response = make_response(BOM + requests_csv())
    else:
        requests_csv_data = json.loads(get_data_from_django(DJANGO_GET_CSV_DATA_URL % (test_id, 'requests')))
        response = make_response(BOM + requests_csv_data)
    file_name = "requests_{0}.csv".format(time())
    disposition = "attachment;filename={0}".format(file_name)
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-disposition"] = disposition
    return response


@app.route("/stats/distribution/csv/<test_id>")
def distribution_stats_csv(test_id):
    BOM = '\uFEFF'
    if locust_runner_id == test_id:
        response = make_response(BOM + distribution_csv())
    else:
        requests_csv_data = json.loads(get_data_from_django(DJANGO_GET_CSV_DATA_URL % (test_id, 'distribution')))
        response = make_response(BOM + requests_csv_data)
    file_name = "distribution_{0}.csv".format(time())
    disposition = "attachment;filename={0}".format(file_name)
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-disposition"] = disposition
    return response


@app.route("/exceptions")
def exceptions():
    if locust_runner_id is None:
        return jsonify({'exceptions': []})
    return jsonify({
        'exceptions': [
            {
                "count": row["count"],
                "msg": row["msg"],
                "traceback": row["traceback"],
                "nodes": ", ".join(row["nodes"])
            } for row in six.itervalues(runners.locust_runner.exceptions)
        ]
    })


@app.route("/exceptions/csv")
def exceptions_csv():
    data = StringIO()
    writer = csv.writer(data)
    writer.writerow(["Count", "Message", "Traceback", "Nodes"])
    for exc in six.itervalues(runners.locust_runner.exceptions):
        nodes = ", ".join(exc["nodes"])
        writer.writerow([exc["count"], exc["msg"], exc["traceback"], nodes])

    data.seek(0)
    response = make_response(data.read())
    file_name = "exceptions_{0}.csv".format(time())
    disposition = "attachment;filename={0}".format(file_name)
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-disposition"] = disposition
    return response


if __name__ == '__main__':
    # 初始化测试实例状态 (未运行)
    update_running_status(DJANGO_GET_UPDATE_RUNNING_STATUS_URL)
    app.run(host='0.0.0.0', port=PORT, debug=True)
