# LEM copyright 2020, All rights reserved. For internal use only

# The aim of this script is to create test runs after automatic tests execution
# Prerequisites:
# - TestRun contain only TestCase (please take care to avoid folders in TestRun)
# - User Jenkins should be present in the project and have sufficient rights

import requests
import json
from conftest import *
cb_rest_url           = "https://lem.codebeamer.com/rest"
auth_account          = 'Jenkins'
auth_password         = 'PassJenkins'

def codebeamer_JSON_to_dict(data):
    if data != b'':
        # convert JSON response to dictionary
        valid_json_string = data.decode('utf-8')
        return json.loads(valid_json_string)
    else:
        return {}

def http_get( url, log=True):
    # User must have the REST API access rights
    try:
        response = requests.get(f"{cb_rest_url}{url}", auth=(auth_account, auth_password))
    except Exception as err:
        ret = {}
    else:
        if response.status_code != 200:
            ret = {}
        else:
            ret = codebeamer_JSON_to_dict(response.content)
            if log:
                pass
    return ret

def http_post(url, data_dict, log=True):
    data_json = json.dumps(data_dict)
    try:
        response = requests.post(f"{cb_rest_url}{url}", headers={'Content-Type': 'application/json; charset=UTF-8'},
                                 data=data_json, auth=(auth_account, auth_password))
    except Exception as err:
        ret = {}
    else:
        if response.status_code not in [200, 201]: # 201=Created

            ret = {}
        else:
            ret = codebeamer_JSON_to_dict(response.content)
            if log:
                pass
    return ret


if __name__ == "__main__":
    pass