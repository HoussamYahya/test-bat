import sys
sys.path.append('C:\\Projets\\Volvo\\Bootloader\\pythontestbench\\Libs')
import Libs.NI_8012 as NI_8012
import Libs.canStatistics as cs
from pytest import fixture


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
