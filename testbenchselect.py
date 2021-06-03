import traceback
import Libs.NI_8012 as NI_8012
from pytest import mark
import pytest

PS_dig_io_bat24V = 'dig/1'
PS_dig_io_bat12V = 'dig/2'
PS_dig_io_refZero = 'dig/3'
PS_dig_io_simu_temp = 'dig/4'
PS_dig_io_simu_current = 'dig/6'
SCANIA_WAKE_LINE = 'dig/7'
PS_dig_io_bat24V_BAT2_BAT3 = 'dig/5'
PS_dig_io_bat12V_BAT2_BAT3 = 'dig/0'

def man_testbench(virtual_bench):
    """
        select the MAN test bench for test
        the power supply is OFF
    """
    virtual_bench.dig_io.write(PS_dig_io_bat24V, {True})
    virtual_bench.dig_io.write(PS_dig_io_bat12V, {True})
    virtual_bench.digital_set_line_output(PS_dig_io_refZero, {True})
    virtual_bench.dig_io.write(PS_dig_io_simu_current, {True})
    virtual_bench.dig_io.write(PS_dig_io_simu_temp, {True})
    virtual_bench.digital_set_line_output(SCANIA_WAKE_LINE, {True})

def volvo_testbench(virtual_bench):
    """
        select the volvo test bench for test
        the power supply is OFF
    """
    virtual_bench.digital_set_line_output(PS_dig_io_bat24V, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_bat12V, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_refZero, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_simu_current, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_simu_temp, {False})
    virtual_bench.digital_set_line_output(SCANIA_WAKE_LINE, {False})

def volvo_BAT3_testbench(virtual_bench):
    """
        select the volvo test bench for test
        the power supply is OFF
    """
    virtual_bench.digital_set_line_output(PS_dig_io_bat24V, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_bat12V, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_refZero, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_simu_current, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_simu_temp, {False})
    virtual_bench.digital_set_line_output(SCANIA_WAKE_LINE, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_bat12V_BAT2_BAT3, {True})
    virtual_bench.digital_set_line_output(PS_dig_io_bat24V_BAT2_BAT3, {True})

def volvo_BAT2_testbench(virtual_bench):
    """
        select the volvo test bench for test
        the power supply is OFF
    """
    virtual_bench.digital_set_line_output(PS_dig_io_bat24V, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_bat12V, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_refZero, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_simu_current, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_simu_temp, {False})
    virtual_bench.digital_set_line_output(SCANIA_WAKE_LINE, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_bat12V_BAT2_BAT3, {False})
    virtual_bench.digital_set_line_output(PS_dig_io_bat24V_BAT2_BAT3, {False})

def bench_select(virtual_bench, project):
    """
    :param project: MAN or VOLVO
    :return:
    """
    if project == 'MAN':
        man_testbench(virtual_bench)
    if project == 'VOLVO_bat2':
        volvo_BAT2_testbench(virtual_bench)
    if project == 'VOLVO_bat3':
        volvo_BAT3_testbench(virtual_bench)

if __name__ == "__main__":
    pass
    #bench_select(virtual_bench, "MAN")