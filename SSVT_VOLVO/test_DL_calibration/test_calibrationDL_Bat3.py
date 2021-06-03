import Libs.NI_8012 as NI_8012
from pytest import mark
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT
from functools import wraps
from pytest_html import extras
from testbenchselect import *

NI_VIRTUAL_BENCH_NAME = "VB8012-31A1DBE"
path = "..\\..\\tools\\Bootconsole\\"
program = "BootConsole.exe"
argument2 = "0"
argument3_1 = "G16001C-Volvo-Application_BWC1.sx"
argument3_2 = "G16001C-Volvo-Application_BWC2.sx"
argument3 = argument3_1
argument4 = "0"
argument5 = "0"
argument6 = "0"
argument7 = "0x1B"

@mark.download_cal_bat3_smoke
class TestDownload:
    @mark.parametrize(
        ("cal_part", "lin_node_address"), [
        ("G16001C-Volvo-Application_BWC1.sx", "0x46"),
        ("G16001C-Volvo-Application_BWC1.sx", "0x47"),
        ("G16001C-Volvo-Application_BWC2.sx", "0x46"),
        ("G16001C-Volvo-Application_BWC2.sx", "0x47"),
    ] )
    def test_download_calibration_bat3(self, virtual_bench, cal_part, lin_node_address, request):
        """
        Test the calibration parameter via BootConsole application
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param index: number of repetition
        :return:
        """
        volvo_BAT3_testbench(virtual_bench)
        request.node._bc_tc_tracker_id = "/item/129162"

        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(4)

        self.execute_sendUncondFrame()
        # time.sleep(2)
        result = self.execute_bootconsole_bwc_calibration(cal_part, lin_node_address)
        assert (result == "'Download Success'")
        if result != "'Download Success'":
            print(1)
            assert (False, "BWC Calibration Download application fail")

    @staticmethod
    def __set_voltages(virtual_bench, voltage):
        """
        Set both power supply voltages to the same value
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param voltage: voltage to be set
        :return:
        """
        virtual_bench.ps_configure_output(NI_8012.PS_25V_POS, voltage, 0.2)
        virtual_bench.ps_configure_output(NI_8012.PS_25V_NEG, -voltage, 0.2)

    @staticmethod
    def execute_bootconsole_bwc_calibration(sel_cal, linadress):

        result = subprocess.run([path + program, "calib", argument2, path + argument3, argument4, argument5, argument6, linadress]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
        to_print = result.stdout.splitlines()
        return str(to_print[-1]).replace('b', '')

    @staticmethod
    def execute_sendUncondFrame():
        str = [path + program, "sendUncondFrame"]
        print(str)
        result = subprocess.run([path + program, "sendUncondFrame"]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
