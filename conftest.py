import time

from py.xml import html
import sys
import os
#sys.path.append('C:\\Users\\mlo\\Volvo\\pythontestbench\\Libs')
sys.path.append('C:\\Projet\\Python_bench_Git_Test\\pythontestbench\\Libs')




from Libs.codebeamer.codebeamer_testruns import *
from testbenchselect import *
import Libs.NI_8012 as NI_8012
from Libs.VolvoLinCom import Lin_Peak_For_Volvo
from pytest import fixture
import Libs.canStatistics as cs

@fixture(scope="session")
def virtual_bench():
    """
    Fixture to use when the test needs the NI virtual bench
    :return: virtual bench resource
    """
    vb = NI_8012.virtualBench()
    #bench_select(vb, ecu)
    yield vb
    # Close the interface
    vb.ps_disable()
    vb.release()


@fixture(scope="session")
def app_lin_com():
    linvolvo = Lin_Peak_For_Volvo()
    linvolvo.connect("appLin_Volvo", 1, 1)
    time.sleep(1)
    linvolvo.disconnect()
    time.sleep(1)
    linvolvo.connect("appLin_Volvo", 1, 1)
    linvolvo.set_global_frame_table()
    time.sleep(1)
    linvolvo.delete_schedule_table(0)
    time.sleep(1)
    linvolvo.set_schedule_table(0)
    yield linvolvo
    linvolvo.disconnect()

@mark.optionalhook
def pytest_html_results_table_header(cells):
    cells.insert(2, html.th('CB_TC_Tracker_ID'))

@mark.optionalhook
def pytest_html_results_table_row(report, cells):
    cells.insert(2, html.td(report._bc_tc_tracker_id, class_="col_uri"))

@mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report._bc_tc_tracker_id = getattr(item, '_bc_tc_tracker_id', 0)

def pytest_sessionfinish(session, exitstatus):
    """ Create a test RUN when whole test finished """
    # cb_TRun()
    pass