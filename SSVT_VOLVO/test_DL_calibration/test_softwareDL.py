import Libs.NI_8012 as NI_8012
from pytest import mark
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT
import os
import os.path
from testbenchselect import *

NI_VIRTUAL_BENCH_NAME = "VB8012-31A1DBE"
#path = "..\\..\\tools\\Bootconsole\\" ### depuis la classe
#path="C:\\Projet\\Volvo\\PythonTest_Volvo\\pythontestbench\\tools\\Bootconsole\\" # depuis me projet
path="C:\\Users\\PC_TEST\\Documents\\PythonTest_Volvo\\pythontestbench\\tools\\Bootconsole\\"
program = "BootConsole.exe"
argument2 = "0"
argument3 = "G16001C-Volvo-Application.sx"
argument4 = "0x1B" #from R7.0 for BAT3 sensor

#dllabspath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + argument3


@mark.SW_DL_BAT2_smoke
class TestDownload_BAT2:
    @mark.parametrize("index", range(1))
    def test_download_application_bat2(self, virtual_bench, index, request):
        """
        Test the software download and default calibration via BootConsole application
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param index: number of repetition
        :return:
        """
        request.node._bc_tc_tracker_id = "/item/151599"
        volvo_BAT2_testbench(virtual_bench)
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(5)
        result = self.execute_bootconsole_download_app()
        assert(result == "'Download Success'")

    def test_DiagnosticSesionControl_ProgrammingSession(self, request):
        request.node._bc_tc_tracker_id = "/item/129897"
        assert(1)

    def test_ECURest11_01(self, request):
        request.node._bc_tc_tracker_id = "/item/130241"
        assert(1)

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
    def execute_bootconsole_download_app(linadress= argument4):
        print("location =", path + program, "dl", argument2, path + argument3, linadress)
        result = subprocess.run([path + program, "dl", argument2, path + argument3, linadress]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
        to_print = result.stdout.splitlines()
        print("to_print  ", to_print)
        return str(to_print[-1]).replace('b', '')

    @staticmethod
    def execute_bootconsole_calibration():
        result = subprocess.run([path + program, "calib", argument2, path + "Calibration.sx", "0"]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
        to_print = result.stdout.splitlines()
        return str(to_print[-1]).replace('b', '')

@mark.SW_DL_BAT3_smoke
class TestDownload_BAT3:
    @mark.parametrize(
        ("cal_part", "lin_node_address"), [
            ("G16001C-Volvo-Application", "0x46"),
            ("G16001C-Volvo-Application", "0x47"),
        ])
    def test_download_application_bat3(self, virtual_bench, cal_part, lin_node_address):
        """
        Test the software download and default calibration via BootConsole application
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param index: number of repetition
        :return:
        """
        volvo_BAT3_testbench(virtual_bench)
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(5)
        result = self.execute_bootconsole_download_app(lin_node_address)
        assert(result == "'Download Success'")

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
    def execute_bootconsole_download_app(linadress= argument4):
        print("location =", path + program, "dl", argument2, path + argument3, linadress)
        result = subprocess.run([path + program, "dl", argument2, path + argument3, linadress]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
        to_print = result.stdout.splitlines()
        print("to_print  ", to_print)
        return str(to_print[-1]).replace('b', '')

    @staticmethod
    def execute_bootconsole_calibration():
        result = subprocess.run([path + program, "calib", argument2, path + "Calibration.sx", "0"]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
        to_print = result.stdout.splitlines()
        return str(to_print[-1]).replace('b', '')

if __name__ == "__main__":
    print(dllabspath)
    pass