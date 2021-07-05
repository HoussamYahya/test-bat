# LEM copyright 2020, All rights reserved. For internal use only
from Libs.codebeamer.codebeamer import *
from bs4 import BeautifulSoup
from conftest import *
import pytest
from datetime import datetime
import time

report = "C:\\Projet\\Volvo\\PythonTest_Volvo\\report.html"

MAN_tracker_test_runs = "403596"   # Tracker Test Runs


def main_cb_testruns(list_TC, subject, current_date, link_to_zip_file):
    # The aim of this script is to create test runs after automatic tests execution
    # Prerequisites:
    # - TestRun contain only TestCase (please take care to avoid folders in TestRun)
    # - User Jenkins should be present in the project and have sufficient rights

    if len(list_TC) > 0:
        for TC in list_TC:
            TC['uri'] = TC['CB_URI']

        # 1. POST /item {"name":"1","tracker":"/tracker/2244","result":"Passed","description":"[{ PieChart title='Test Result' threed='true' seriespaint='GREEN,RED' \n\nSuccessful, 1\nFailure, 0\n}]",
        #                "descFormat":"Wiki","submitter":{"uri":"/user/self"},"testConfiguration":{"uri":"/item/16266"},"testSet":{"uri":"/item/112892"},
        #                "testCases":[[{"uri":"/item/112896"},true,true,""]]}
        list_testCases = []
        for TC in list_TC:
            if TC['uri'] != None:
                list_testCases.append([TC['uri'], False, False, ""])  # uri, Active?, Stop on Failure?, Result
        global_testrun_result = 'Passed' if all(TC['Passed'] != 0 for TC in list_TC) else 'Failed'
        data_dict = {"name": f"{subject} on {current_date}",
                     "tracker": f"/tracker/{MAN_tracker_test_runs}",
                     "description": "Test run automatically generated",
                     "submitter": {"uri": "/user/self"},
                     'runOnlyAcceptedTestCases': False,
                     "testCases": list_testCases,
                     'result': global_testrun_result,
                     }
        ret = http_post(f"/item", data_dict=data_dict, log=True)
        if 'uri' in ret and '/item/' in ret['uri']:
            testRunId = int(ret['uri'].replace('/item/', ''))
            # 2. POST /item {"name":"fullName","tracker":"/tracker/2244","result":"Passed","description":"--","submitter":{"uri":"/user/self"},"parent":{"uri":"/item/112899"},
            #                "testConfiguration":{"uri":"/item/16266"},"testSet":{"uri":"/item/112892"},"testCases":[[{"uri":"/item/112896"},true,true,""]]}
            for TC in list_TC:
                if TC['uri'] != None:
                    if TC['Failed'] != 0:
                        result = 'Failed'
                    elif TC['Passed'] != 0:
                        result = 'Passed'
                    else:
                        result = 'Blocked'

                    newline = '\r\n\r\n'
                    data_dict = {"name": f"{TC['TC name']}",
                                 "tracker": f"/tracker/{MAN_tracker_test_runs}",
                                 "result": result,
                                 "description": f"TestSheet: {TC['TS']}{newline}[Direct link to trace |file:{link_to_zip_file}]",
                                 "descFormat": "Wiki",
                                 "submitter": {"uri": "/user/self"},
                                 'parent': f'/item/{testRunId}',
                                 'status': 'Finished',
                                 'spentMillis': TC['duration'] * 1000,
                                 "testCases": [[TC['uri'], False, False, ""]]}
                    ret = http_post(f"/item", data_dict=data_dict, log=True)
                    testRun_child_Id = int(ret['uri'].replace('/item/', ''))

        else:
            pass


def cb_TRun():
    print("start create TEST RUN")
    list_TC = []
    f_report_html = open(report, "rb")
    report_parse = BeautifulSoup(f_report_html, 'html.parser')

    for TC_Result, CB_URI, TC_DURATION, TC_Name in zip(report_parse.find_all('td', "col-result" ), report_parse.find_all('td', "col_uri"), report_parse.find_all('td', "col-duration"), report_parse.find_all('td', "col-name" )):
        if TC_Result.contents[0] == 'Passed':
            ret_test_pos = 1
            ret_test_neg = 0
        else:
            ret_test_pos = 0
            ret_test_neg = 1
        list_TC.append({'TC name': str(TC_Name.contents[0]),'CB_URI' : str(CB_URI.contents[0]), "Passed": ret_test_pos, 'Failed' : ret_test_neg, 'TS': "VOVLO NON REGRESSION", 'duration': float(TC_DURATION.contents[0])})
    print(list_TC)
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    main_cb_testruns(list_TC, subject=f"Test RUN after Non Regression execution", current_date=current_date, link_to_zip_file="Not available")

if __name__ == '__main__':
    cb_TRun()