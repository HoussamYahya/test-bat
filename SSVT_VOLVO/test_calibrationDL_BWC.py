import Libs.NI_8012 as NI_8012
from pytest import mark
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT

NI_VIRTUAL_BENCH_NAME = "VB8012-31A1DBE"
path = "C:\\Users\\mlo\\Volvo\\dll_bootloader\\x64\\Release\\"
program = "BootConsole.exe"
argument2 = "0"
argument3_1 = "G16001C-Volvo-Application_BWC1.sx"
argument3_2 = "G16001C-Volvo-Application_BWC2.sx"
argument3   = argument3_1
argument4 = "bwc"



@mark.download_app_cal_bwc
class TestDownload:
    @mark.parametrize("index",        range(100))
    def test_download_calibration_bwc(self, virtual_bench, index):
        """
        Validate the periods of the CAN frames after reset of the sensor
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param index: number of repetition
        :return:
        """
        if ((index%2) == 0):
            sel_cal = 2
        else:
            sel_cal = 1

        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(5)
        
        self.execute_sendUncondFrame()
        #time.sleep(2)
        result = self.execute_bootconsole_bwc_calibration(sel_cal)
        assert(result == "'BWC Cal Download Success'")
        # if result != "'Download Success'":
        #     print(1)
        #     assert (False, "BWC Calibration Download application fail")

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
    def execute_bootconsole_bwc_calibration(sel_cal):
        if sel_cal == 1:
            argument3 = argument3_1
        elif sel_cal == 2:
            argument3 = argument3_2
        result = subprocess.run([path + program, "calib", argument2, path + argument3, argument4]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
        to_print = result.stdout.splitlines()
        return str(to_print[-1]).replace('b', '')

    @staticmethod
    def execute_sendUncondFrame():
        str = [path + program, "sendUncondFrame"]
        print(str)
        result = subprocess.run([path + program, "sendUncondFrame"]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
                   

