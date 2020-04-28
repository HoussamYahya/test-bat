import Libs.NI_8012 as NI_8012
from pytest import mark
import time
import asyncio
import can

NMOSEK_WAKEUP_REASON_MASK_LOCAL = 1
NMOSEK_WAKEUP_REASON_MASK_CAN = 2

NMOSEK_STAY_AWAKE_REASON_MASK_LOCAL = 1
NMOSEK_STAY_AWAKE_REASON_MASK_CAN = 2
NMOSEK_STAY_AWAKE_REASON_MASK_TIMER_NOT_EXPIRED = 4

NMOSEK_OPCODE_ALIVE_NO_SLEEP = 2
NMOSEK_OPCODE_ALIVE_SLEEP = 6
NMOSEK_OPCODE_RING_NO_SLEEP = 1
NMOSEK_OPCODE_RING_SLEEP_NO_ACK = 5
NMOSEK_OPCODE_RING_SLEEP_WITH_ACK_1 = 3
NMOSEK_OPCODE_RING_SLEEP_WITH_ACK_2 = 7
NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP = 0
NMOSEK_OPCODE_LIMP_HOME_SLEEP = 4

NMOSEK_TIMER_T_TYP_MIN = 0.070
NMOSEK_TIMER_T_TYP_MAX = 0.110
NMOSEK_TIMER_T_MAX_MIN = 0.220
NMOSEK_TIMER_T_MAX_MAX = 0.284
NMOSEK_TIMER_T_ACTIVE_MIN = 4.000
NMOSEK_TIMER_T_ERROR = 1
NMOSEK_TIMER_T_ERROR_MIN = 0.950
NMOSEK_TIMER_T_ERROR_MAX = 1.050
NMOSEK_TIMER_T_LIMP_HOME_MIN = 3.500
NMOSEK_TIMER_T_LIMP_HOME_MAX = 4.500
NMOSEK_TIMER_T_LIMP_HOME_DTC_MIN = 2.000
NMOSEK_TIMER_T_LIMP_HOME_DTC_MAX = 3.500
NMOSEK_TIMER_T_WBS = 5
NMOSEK_TIMER_T_WBS_MIN = 4.950
NMOSEK_TIMER_T_WBS_MAX = 5.050

NMOSEK_RX_LIMIT = 4
NMOSEK_TX_LIMIT = 8

NMOSEK_OWN_ADDRESS = 0xF4
NMOSEK_ADDRESS_IC = 0x17
NMOSEK_CAN_ID_IC = 0x18FFB000 + NMOSEK_ADDRESS_IC
SLEEP_FILTER_TIME = 60

@mark.parametrize("frame_id", [0x18FC0AF4, 0x18FC08F4])
@mark.voltage_after_wakeup
#def test_voltages_after_wakeup(can_interface, frame_id):
def test_voltages_after_wakeup(virtual_bench, can_interface, frame_id):
    """
    Check that the voltage are stable after wakeup
    :param virtual_bench: fixture of pytest to use the NI virtual bench
    :param can_interface: fixture of pytest to use CAN interface
    :return:
    """
    # Start the sensor and wait for the sleep mode
    virtual_bench.ps_configure_output(NI_8012.PS_25V_POS, 12.0, 0.1)
    virtual_bench.ps_configure_output(NI_8012.PS_25V_NEG, -12.0, 0.1)
    virtual_bench.ps_generate_por()
    time.sleep(70)
    # Purge Rx frames
    can_interface.reset()
    # Wakeup the sensor
    message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                          data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
    can_interface.send_frame(message)
    # Read the values of the voltages
    can_interface.receive_all_not_async(number_of_frames=40, frame_id=frame_id, extended=True)
    for rxFrame in can_interface.rx_frames:
        voltage = (rxFrame.data[3] + 256 * rxFrame.data[4]) / 20.0
        print(f'VOLT = {voltage}')
