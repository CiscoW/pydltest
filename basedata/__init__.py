import uuid

default_app_config = 'basedata.apps.BaseDataConfig'


def get_uuid():
    return str(uuid.uuid1()).replace("-", "")
