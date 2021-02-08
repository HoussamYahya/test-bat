import sys
sys.path.append('C:\\Projets\\Volvo\\Bootloader\\pythontestbench\\Libs')
import NI_8012 as NI_8012
from pytest import mark
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT

NI_VIRTUAL_BENCH_NAME = "VB8012-31A1DBE"
#path = "C:\\software\\AutomotiveCommon\\bootconsole\\dll_bootloader\\x64\\Debug\\"
path = "C:\\Projets\\Volvo\\Bootloader\\dll_bootloader\\x64\\Debug\\"
program = "BootConsole.exe"
argument1 = "dl"
argument2 = "0"
argument3 = "G16001C-Volvo-Application.sx"
stantby_current_conso = 0,02


@mark.statemachine
class TestDownload:
    #@mark.parametrize("index",        range(100))
    def test_T_Operational_To_Standby(self, virtual_bench):
        """
        Validate the periods of the CAN frames after reset of the sensor
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param index: number of repetition
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(5)
        
        #start Lin communication
        #Check activities in the lin bus
        
        #stop the Lin communication
        #Check activities in the lin bus
        #check the power consumtion under threshold
        
        current_PS_25V_NEG = ps_get_current_consumption(PS_25V_NEG)
        assert(current_PS_25V_NEG < stantby_current_conso)
        
        current_PS_25V_POS = ps_get_current_consumption(PS_25V_POS)        
        assert(current_PS_25V_POS < stantby_current_conso)

    @staticmethod
    def __set_voltages(virtual_bench, voltage):
        """
        Set both power supply voltages to the same value
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param voltage: voltage to be set
        :return:
        """
        virtual_bench.ps_configure_output(NI_8012.PS_25V_POS, voltage, 0.2)
        virtual_bench.ps_configure_output(NI_8012.PS_25V_NEG, 0, 0.2)

    @staticmethod
    def execute_bootconsole():
        str = [path + program, argument1, argument2, path + argument3]
        print(str)
        result = subprocess.run([path + program, argument1, argument2, path + argument3]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
        to_print = result.stdout.splitlines()
        print()
        print(to_print)
        print()

        zz = to_print[-1]
        print()
        print(zz)
        print()

        #return str(to_print[-1]).replace('b', '')
        #return str(to_print)
        return (zz.decode('utf-8'))
