'''
Created on Dec 9, 2020

@author: ext_say
'''
import sys, os
import Libs.NI_8012 as NI_8012
from pytest import mark
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT


NI_VIRTUAL_BENCH_NAME = "VB8012-31D7496"
path = "C:\\Users\\ext_say\\Volvo\\dll_bootloader\\x64\\Debug" # the path sall be change
program = "BootConsole.exe"
abs_program = os.path.join(path, program)

sequence = [
#     [abs_program, "rc", "0","DE10","1000"],
    [abs_program, "slcs", "0"],
     
#     RoutineControl RequestResults FilterCurrentAnalog1 (31 03 DE 10)
    [abs_program, "drc", "0","DE10","64"], 
    
#     RoutineControl Start FilterVoltage1 (31 01 DC 01)
    [abs_program, "drc", "0","DC01","3E8"],
#     
# #     RoutineControl Start FilterVoltage2 (31 01 DC 02)
    [abs_program, "drc", "0","DC02","3E8"],
# #     Read by ID IP Gain
    [abs_program, "drd", "0", "0A01","X"],
#     
# #     Read by ID IP Gain
    [abs_program, "dwd", "0", "0101","D", "5", "517"],
#     
# #     Read by ID IP Offset
    [abs_program, "drd", "0", "0102","X"],
#     
# #     Read by ID IP Offset
    [abs_program, "dwd", "0", "0102","D", "5", "12"]
    ]

def find_positive_resp(byte_list):
    """
    Validate the periods of the CAN frames after reset of the sensor
    :param byte_list: List of string in byte format
    :return: 'OK' if positive response  or 'KO' if it negative
    """
    res = "KO"
    for x in byte_list:
        x = x.decode("utf-8")
        if  (x.find("Positive response") >= 0) or \
            (x.find("positive response") >= 0):
            res = "OK"
    return res

@mark.dv_test
class TestDownload:
    @mark.parametrize("index",        range(1))
    def test_dv_test(self, virtual_bench, index):
        """
        Validate the periods of the CAN frames after reset of the sensor
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param index: number of repetition
        :return:
        """
        
        self.__set_voltages(virtual_bench, 12.5)
        virtual_bench.ps_generate_por()
#         virtual_bench.ps_enable()
        time.sleep(10)

        result = self.execute_bootconsole()
        assert(result == 'OK')

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
    def execute_bootconsole():
        res = "KO"
        result = None
        for cmd in sequence:
            result = subprocess.run(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
            res = find_positive_resp(result.stdout.splitlines())
            time.sleep(5)
        return res
