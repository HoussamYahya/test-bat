import Libs.NI_8012 as NI_8012
from pytest import mark
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT

NI_VIRTUAL_BENCH_NAME = "VB8012-31A1DBE"
path = "C:\\software\\AutomotiveCommon\\bootconsole\\dll_bootloader\\x64\\Debug\\"
program = "BootConsole.exe"
argument2 = "0"
argument3 = "G16001C-Volvo-Application.sx"


@mark.download_app_cal
class TestDownload:
    @mark.parametrize("index",        range(1))
    def test_download_application(self, virtual_bench, index):
        """
        Validate the periods of the CAN frames after reset of the sensor
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param index: number of repetition
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(5)
        result = self.execute_bootconsole_download()
        print(result)
        # if result != "'Download Success'":
        #     print(1)
        #     assert (False, "Download application fail")
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(5)
        result = self.execute_bootconsole_calibration()
        print(result)
        # if result != "'Download Success'":
        #     print(2)
        #     assert (False, "Download calibration fail")
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
    def execute_bootconsole_download():
        result = subprocess.run([path + program, "dl", argument2, path + "G16001C-Volvo-Application.sx"]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
        to_print = result.stdout.splitlines()
        return str(to_print[-1]).replace('b', '')

    @staticmethod
    def execute_bootconsole_calibration():
        result = subprocess.run([path + program, "calib", argument2, path + "Calibration.sx", "0"]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
        to_print = result.stdout.splitlines()
        return str(to_print[-1]).replace('b', '')
