import sys
import os
#sys.path.append('C:\\Users\\mlo\\Volvo\\pythontestbench\\Libs')
sys.path.append('C:\\Projet\\Python_bench_Git_Test\\pythontestbench\\Libs')
import Libs.NI_8012 as NI_8012
import Libs.canStatistics as cs
from pytest import fixture
from VolvoLinCom import Lin_Peak_For_Volvo
import time


@fixture(scope="session")
def virtual_bench():
    """
    Fixture to use when the test needs the NI virtual bench
    :return: virtual bench resource
    """
    vb = NI_8012.virtualBench()
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