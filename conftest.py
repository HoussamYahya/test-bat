from py.xml import html
import sys
import os
#sys.path.append('C:\\Users\\mlo\\Volvo\\pythontestbench\\Libs')
sys.path.append('C:\\Projet\\Python_bench_Git_Test\\pythontestbench\\Libs')

import Libs.NI_8012 as NI_8012
import Libs.canStatistics as cs
from pytest import fixture
from Libs.codebeamer.codebeamer_testruns import *
from testbenchselect import *


@fixture(scope="session")
def virtual_bench():
    """
    Fixture to use when the test needs the NI virtual bench
    :return: virtual bench resource
    """
    vb = NI_8012.virtualBench()
    bench_select(vb, "VOLVO")
    yield vb
    # Close the interface
    vb.ps_disable()
    vb.release()


@fixture(scope="function")
def can_interface():
    """
    Fixture to use when the test needs a CAN interface
    :return: can interface resource
    """
    can = cs.canStatistics(bitrate=250000)
    yield can
    can.bus.shutdown()

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
    cb_TRun()