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


@mark.can_nmosek
class Test_can_nmosek:
    """
    Validation of the NMOSEK state machine
    List of the transitions and the test validating the transition
    Generic - test_nmosek_frame_id, test_nmosek_frame_dlc
    (1) - test_first_frame_send_by_sensor_after_por, test_first_frame_send_by_sensor_after_wakeup
    (2) - test_nmosek_alone_on_network
    (3) - test_nmosek_alone_on_network, test_normal_mode_to_skipped, test_normal_mode_to_breakdown
    (4) - test_ring_to_sleep
    (5) - test_pre_sleep_to_normal
    (6) - test_break_down_while_pre_sleep, test_skipped_while_pre_sleep
    (7) -
    (8) - test_ring_to_sleep
    (9) - test_wait_bus_sleep_to_reset_NM_no_SI, test_wait_bus_sleep_to_reset_local_wakeup
    (10)- test_nmosek_alone_on_network
    (11)- test_no_can_ack_sleep_mode
    (12)- test_limp_home_to_nm_reset_with_can, test_limp_home_to_nm_reset_local_wakeup
    (13)- test_nmosek_sensor_alone_going_to_sleep
    (14)- test_limp_home_pre_sleep_to_limp_home_local_wakeup, test_limp_home_pre_sleep_to_limp_home_can
    (15)- test_limp_home_to_wait_bus_sleep
    (16)- test_wait_bus_sleep_to_limp_home_local_wakeup, test_wait_bus_sleep_to_limp_home_can
    (17)- test_nmosek_sensor_alone_going_to_sleep
    (18)- test_wait_bus_sleep_to_limp_home_pre_sleep
    (19)- test_nmosek_sensor_alone_going_to_sleep
    (20)- test_first_frame_after_wakeup_is_nmosek, test_wakeup_from_can_frame
    (21)-
    (22)-

    timing checks:
    (TTyp) - test_nmosek_alone_on_network
    (TMax) - test_nmosek_alone_on_network
    (TActiveMin) - test_wait_bus_sleep_to_reset_NM_no_SI
    (TLimpHome) - not testable because sleep conditions are filtered for longer than TLimpHome
    (TError) - test_nmosek_alone_on_network
    (TWbs) - test_ring_to_sleep, test_nmosek_sensor_alone_going_to_sleep
    """
    def test_nmosek_frame_id(self, virtual_bench, can_interface):
        """
        Validate CAN frame id for NM OSEK is correct
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 13.0)
        virtual_bench.ps_generate_por()
        rx_stats = can_interface.get_period(0x18FFB0F4, 5, extended=True)
        # Check at least one frame has been received
        assert rx_stats is not None

    def test_nmosek_frame_dlc(self, virtual_bench, can_interface):
        """
        Validate CAN frame dlc for NM OSEK is correct
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 13.0)
        virtual_bench.ps_generate_por()
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.dlc == 8

    def test_first_frame_send_by_sensor_after_por(self, virtual_bench, can_interface):
        """
        Check that the first frame sent by sensor after POR is a NMOSEK frame
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 13.0)
        virtual_bench.ps_disable()
        asyncio.run(self.__power_on_and_get_frames(virtual_bench, can_interface, number_of_frames=5))
        assert can_interface.rx_frames[0].arbitration_id == 0x18FFB0F4

    def test_nmosek_alone_on_network(self, virtual_bench, can_interface):
        """
        Validate CAN frame for NM OSEK when the sensor is alone on the network
        Test based on figure 2-7 on FAW CAN communication part 2 specification
        It validates transition 2, 3 and 10
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 13.0)
        virtual_bench.ps_disable()
        asyncio.run(self.__power_on_and_get_frames(virtual_bench, can_interface, frame_id=0x18FFB0F4, number_of_frames=NMOSEK_RX_LIMIT*2+5))
        for i in range(NMOSEK_RX_LIMIT):
            assert can_interface.rx_frames[2*i].data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
            assert can_interface.rx_frames[2*i+1].data[1] == NMOSEK_OPCODE_RING_NO_SLEEP
            assert can_interface.rx_frames[2*i].data[0] == NMOSEK_OWN_ADDRESS
            assert can_interface.rx_frames[2*i+1].data[0] == NMOSEK_OWN_ADDRESS
            periodTTyp = can_interface.rx_frames[2*i+1].timestamp - can_interface.rx_frames[2*i].timestamp
            assert NMOSEK_TIMER_T_TYP_MIN < periodTTyp < NMOSEK_TIMER_T_TYP_MAX
            if i > 0:
                periodTMax = can_interface.rx_frames[2*i].timestamp - can_interface.rx_frames[2*i-1].timestamp
                assert NMOSEK_TIMER_T_MAX_MIN < periodTMax < NMOSEK_TIMER_T_MAX_MAX
        periodTMax = can_interface.rx_frames[2 * NMOSEK_RX_LIMIT].timestamp - can_interface.rx_frames[2 * NMOSEK_RX_LIMIT - 1].timestamp
        assert NMOSEK_TIMER_T_MAX_MIN < periodTMax < NMOSEK_TIMER_T_MAX_MAX
        assert can_interface.rx_frames[2 * NMOSEK_RX_LIMIT].data[0] == NMOSEK_OWN_ADDRESS
        assert can_interface.rx_frames[2 * NMOSEK_RX_LIMIT].data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
        for i in range(2*NMOSEK_RX_LIMIT+1, 2*NMOSEK_RX_LIMIT + 4):
            assert can_interface.rx_frames[i].data[0] == NMOSEK_OWN_ADDRESS
            assert can_interface.rx_frames[i].data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
            period = can_interface.rx_frames[i].timestamp - can_interface.rx_frames[i - 1].timestamp
            assert NMOSEK_TIMER_T_ERROR_MIN < period < NMOSEK_TIMER_T_ERROR_MAX

    def test_nmosek_sensor_alone_going_to_sleep(self, virtual_bench, can_interface):
        """
        Check that the sensor goes to sleep mode in the correct way of NMOSEK if alone on the netwrok
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0) # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_disable()
        asyncio.run(self.__power_on_and_get_frames(virtual_bench, can_interface, frame_id=0x18FFB0F4,
                                                   number_of_frames=SLEEP_FILTER_TIME/NMOSEK_TIMER_T_ERROR + 2*NMOSEK_RX_LIMIT,
                                                   timeout=70.0))
        # At that point the timeout has triggered and the sensor should be asleep
        # Check the last frame sent on NMOSEK is a sleep indication
        if can_interface.rx_frames[-1].data[1] != NMOSEK_OPCODE_LIMP_HOME_SLEEP:
            # There could be a one frame jitter on the rx of the sleep indication
            newFrame = can_interface.read_frame(0x18FFB0F4, extended=True, timeout=2.0)
            assert newFrame.data[1] == NMOSEK_OPCODE_LIMP_HOME_SLEEP
        else:
            assert can_interface.rx_frames[-1].data[1] == NMOSEK_OPCODE_LIMP_HOME_SLEEP
        self.__check_wait_bus_sleep_and_bus_sleep(virtual_bench, can_interface)

    def test_first_frame_after_wakeup_is_nmosek(self, virtual_bench, can_interface):
        """
        Check that the first frame sent by sensor after wakeup is an NMOSEK frame
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(70)
        can_interface.reset()
        self.__set_voltages(virtual_bench, 14.0)
        rx_frame = can_interface.read_frame(None, extended=True)
        assert rx_frame.arbitration_id == 0x18FFB0F4
        assert rx_frame.data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
        assert rx_frame.data[0] == NMOSEK_OWN_ADDRESS

    def test_wakeup_from_can_frame(self, virtual_bench, can_interface):
        """
        Check that sensor is able to wakeup with any message
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(70)
        asyncio.run(self.__wakeup_with_can_frame_and_get_frames(virtual_bench, can_interface))
        assert can_interface.rx_frames[0].arbitration_id == 0x18FFB0F4
        assert can_interface.rx_frames[0].data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
        assert can_interface.rx_frames[0].data[0] == NMOSEK_OWN_ADDRESS

    @staticmethod
    def __creation_of_the_ring(can_interface):
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_ADDRESS_IC, NMOSEK_OPCODE_ALIVE_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        can_interface.reset()
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        if rx_frame.data[0] == NMOSEK_OWN_ADDRESS:
            can_interface.send_frame(message)
            can_interface.reset()
            rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        return rx_frame

    def test_creation_of_the_ring(self, virtual_bench, can_interface):
        """
        Check the creation of a ring message
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        # Start the sensor
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(1.0)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        # Simulate IC
        rx_frame = self.__creation_of_the_ring(can_interface)
        assert rx_frame.data[0] == NMOSEK_ADDRESS_IC
        can_interface.receive_all_not_async(extended=True, frame_id=0x18FFB0F4)
        for i in range(NMOSEK_RX_LIMIT):
            assert can_interface.rx_frames[2*i].data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
            assert can_interface.rx_frames[2*i+1].data[1] == NMOSEK_OPCODE_RING_NO_SLEEP
            assert can_interface.rx_frames[2*i].data[0] == NMOSEK_OWN_ADDRESS
            assert can_interface.rx_frames[2*i+1].data[0] == NMOSEK_OWN_ADDRESS
        assert can_interface.rx_frames[2 * NMOSEK_RX_LIMIT].data[0] == NMOSEK_OWN_ADDRESS
        assert can_interface.rx_frames[2 * NMOSEK_RX_LIMIT].data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
        for i in range(2*NMOSEK_RX_LIMIT+1, 2*NMOSEK_RX_LIMIT + 4):
            assert can_interface.rx_frames[i].data[0] == NMOSEK_OWN_ADDRESS
            assert can_interface.rx_frames[i].data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP

    def __start_ring_for_10_loops(self, can_interface):
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_ADDRESS_IC, NMOSEK_OPCODE_ALIVE_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        can_interface.reset()
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        if rx_frame.data[0] == NMOSEK_OWN_ADDRESS:
            can_interface.send_frame(message)
            can_interface.reset()
            rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[0] == NMOSEK_ADDRESS_IC
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        counter = 0
        while counter < 10:
            rx_frame = self.__wait_and_send_IC_ring_message(can_interface)
            counter += 1

    def test_normal_mode_to_skipped(self, virtual_bench, can_interface):
        """
        Check the normal mode then skipped
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(1.0)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        # Simulate IC
        self.__start_ring_for_10_loops(can_interface)
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_ADDRESS_IC, NMOSEK_OPCODE_ALIVE_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
        assert rx_frame.data[0] == NMOSEK_OWN_ADDRESS

    def test_normal_mode_to_breakdown(self, virtual_bench, can_interface):
        """
        Check the normal mode then breakdown
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(1.0)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        # Simulate IC
        self.__creation_of_the_ring(can_interface)
        # Generate breakdown
        time.sleep(NMOSEK_TIMER_T_MAX_MAX)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
        assert rx_frame.data[0] == NMOSEK_OWN_ADDRESS

    @staticmethod
    def __wait_and_send_IC_ring_message(can_interface):
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        time.sleep(0.1)
        can_interface.send_frame(message)
        return can_interface.read_frame(0x18FFB0F4, extended=True)

    def __start_ring_up_to_sleep(self, can_interface):
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_ADDRESS_IC, NMOSEK_OPCODE_ALIVE_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        can_interface.reset()
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        if rx_frame.data[0] == NMOSEK_OWN_ADDRESS:
            can_interface.send_frame(message)
            can_interface.reset()
            rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[0] == NMOSEK_ADDRESS_IC
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        time_end = time.time() + 70.0
        while rx_frame.data[1] == NMOSEK_OPCODE_RING_NO_SLEEP and time.time() < time_end:
            rx_frame = self.__wait_and_send_IC_ring_message(can_interface)
        assert time.time() < time_end # The sensor has requested a sleep before the timeout

    @mark.parametrize("ackCode",  [NMOSEK_OPCODE_RING_SLEEP_WITH_ACK_1, NMOSEK_OPCODE_RING_SLEEP_WITH_ACK_2])
    def test_ring_to_sleep(self, virtual_bench, can_interface, ackCode):
        """
        Check the sleep from thr ring
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :param ackCode: sleep acknowledgement code for NMOSEK
        :return:
        """
        # Start the sensor
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(1.0)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        self.__start_ring_up_to_sleep(can_interface)
        rx_frame = self.__wait_and_send_IC_ring_message(can_interface)
        assert rx_frame is not None
        assert rx_frame.data[1] == NMOSEK_OPCODE_RING_SLEEP_NO_ACK
        time.sleep(0.1)
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, ackCode, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        self.__check_wait_bus_sleep_and_bus_sleep(virtual_bench, can_interface)

    def test_break_down_while_pre_sleep(self, virtual_bench, can_interface):
        """
        Check the breakdown from pre sleep mode
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(1.0)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        self.__start_ring_up_to_sleep(can_interface)
        rx_frame = self.__wait_and_send_IC_ring_message(can_interface)
        assert rx_frame is not None
        assert rx_frame.data[1] == NMOSEK_OPCODE_RING_SLEEP_NO_ACK
        # Generate breakdown
        time.sleep(NMOSEK_TIMER_T_MAX_MAX)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[1] == NMOSEK_OPCODE_ALIVE_SLEEP
        assert rx_frame.data[0] == NMOSEK_OWN_ADDRESS

    def test_skipped_while_pre_sleep(self, virtual_bench, can_interface):
        """
        Check the breakdown from pre sleep mode
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(1.0)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        self.__start_ring_up_to_sleep(can_interface)
        rx_frame = self.__wait_and_send_IC_ring_message(can_interface)
        assert rx_frame is not None
        assert rx_frame.data[1] == NMOSEK_OPCODE_RING_SLEEP_NO_ACK
        # Generate skipped
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_ADDRESS_IC, NMOSEK_OPCODE_ALIVE_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[1] == NMOSEK_OPCODE_ALIVE_SLEEP
        assert rx_frame.data[0] == NMOSEK_OWN_ADDRESS

    def test_pre_sleep_to_normal(self, virtual_bench, can_interface):
        """
        Check the transition from sleep to normal
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(1.0)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        self.__start_ring_up_to_sleep(can_interface)
        self.__set_voltages(virtual_bench, 14.0)  # Set the power supply so that the sleep conditions are fulfilled
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        time.sleep(0.1)
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[1] == NMOSEK_OPCODE_RING_NO_SLEEP
        assert rx_frame.data[0] == NMOSEK_ADDRESS_IC

    def test_no_can_ack_sleep_mode(self, virtual_bench):
        """
        Check that the sensor can go into sleep mode even if no message are acknowledged
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(70)
        current = virtual_bench.ps_get_current_consumption(NI_8012.PS_25V_NEG)
        assert current < 0.002

    def test_wait_bus_sleep_to_reset_local_wakeup(self, virtual_bench, can_interface):
        """
        Check the transition from wait bus sleep to reset
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(1.0)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        self.__start_ring_up_to_sleep(can_interface)
        rx_frame = self.__wait_and_send_IC_ring_message(can_interface)
        time.sleep(0.1)
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_SLEEP_WITH_ACK_1, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        time.sleep(2)
        asyncio.run(self.__wakeup_with_voltage_and_get_frames(virtual_bench, can_interface))
        assert can_interface.rx_frames[0].arbitration_id == 0x18FFB0F4
        assert can_interface.rx_frames[0].data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
        assert can_interface.rx_frames[0].data[0] == NMOSEK_OWN_ADDRESS

    def test_wait_bus_sleep_to_reset_NM_no_SI(self, virtual_bench, can_interface):
        """
        Check the transition from wait bus sleep to reset
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)  # Set the power supply so that the sleep conditions are fulfilled
        virtual_bench.ps_generate_por()
        time.sleep(1.0)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        self.__start_ring_up_to_sleep(can_interface)
        rx_frame = self.__wait_and_send_IC_ring_message(can_interface)
        time.sleep(0.1)
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_SLEEP_WITH_ACK_1, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        time.sleep(2)
        can_interface.reset()
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        timeReset = time.time()
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.arbitration_id == 0x18FFB0F4
        assert rx_frame.data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
        assert rx_frame.data[0] == NMOSEK_OWN_ADDRESS
        # Check tActiveMin
        self.__start_ring_up_to_sleep(can_interface)
        timeSleep = time.time()
        assert NMOSEK_TIMER_T_ACTIVE_MIN - 0.5 < timeSleep-timeReset < NMOSEK_TIMER_T_ACTIVE_MIN + 0.5

    def test_limp_home_to_nm_reset_with_can(self, virtual_bench, can_interface):
        """
        Check the LimpHome to Reset transition with frame
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        can_interface.receive_all_not_async(number_of_frames=10, frame_id=0x18FFB0F4, extended=True, timeout=20.0)
        assert can_interface.rx_frames[-1].data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
        can_interface.reset()
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.arbitration_id == 0x18FFB0F4
        assert rx_frame.data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
        assert rx_frame.data[0] == NMOSEK_OWN_ADDRESS

    def test_limp_home_to_nm_reset_local_wakeup(self, virtual_bench, can_interface):
        """
        Check the LimpHome to Reset transition with frame and local wakeup
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 14.0)
        virtual_bench.ps_generate_por()
        can_interface.receive_all_not_async(number_of_frames=10, frame_id=0x18FFB0F4, extended=True, timeout=20.0)
        assert can_interface.rx_frames[-1].data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
        can_interface.reset()
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_SLEEP_WITH_ACK_1, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.arbitration_id == 0x18FFB0F4
        assert rx_frame.data[1] == NMOSEK_OPCODE_ALIVE_NO_SLEEP
        assert rx_frame.data[0] == NMOSEK_OWN_ADDRESS

    def test_limp_home_pre_sleep_to_limp_home_local_wakeup(self, virtual_bench, can_interface):
        """
        Check the LimpHome Pre Sleep to LimpHome transition
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        can_interface.receive_all_not_async(number_of_frames=10, frame_id=0x18FFB0F4, extended=True, timeout=20.0)
        assert can_interface.rx_frames[-1].data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        while rx_frame.data[1] != NMOSEK_OPCODE_LIMP_HOME_SLEEP:
            rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        self.__set_voltages(virtual_bench, 14.0)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP

    def test_limp_home_pre_sleep_to_limp_home_can(self, virtual_bench, can_interface):
        """
        Check the LimpHome Pre Sleep to LimpHome transition
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        can_interface.receive_all_not_async(number_of_frames=10, frame_id=0x18FFB0F4, extended=True, timeout=20.0)
        assert can_interface.rx_frames[-1].data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        while rx_frame.data[1] != NMOSEK_OPCODE_LIMP_HOME_SLEEP:
            rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP

    def test_limp_home_to_wait_bus_sleep(self, virtual_bench, can_interface):
        """
        Check the LimpHome Pre Sleep to LimpHome transition
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        can_interface.receive_all_not_async(number_of_frames=10, frame_id=0x18FFB0F4, extended=True, timeout=20.0)
        assert can_interface.rx_frames[-1].data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
        # Go to LimpHome PreSleep
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        while rx_frame.data[1] != NMOSEK_OPCODE_LIMP_HOME_SLEEP:
            rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        # Go back to LimpHome
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
        # Go back to LimpHome
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_SLEEP_WITH_ACK_1, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True, timeout=2.0)
        assert rx_frame is None

    def test_wait_bus_sleep_to_limp_home_local_wakeup(self, virtual_bench, can_interface):
        """
        Check the LimpHome Pre Sleep to LimpHome transition
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        can_interface.receive_all_not_async(number_of_frames=10, frame_id=0x18FFB0F4, extended=True, timeout=20.0)
        assert can_interface.rx_frames[-1].data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
        # Go to LimpHome PreSleep
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        while rx_frame.data[1] != NMOSEK_OPCODE_LIMP_HOME_SLEEP:
            rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        # Go back to LimpHome
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
        # Go back to LimpHome
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_SLEEP_WITH_ACK_1, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True, timeout=2.0)
        assert rx_frame is None
        self.__set_voltages(virtual_bench, 14.0)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True, timeout=2.0)
        assert rx_frame.data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP

    def test_wait_bus_sleep_to_limp_home_can(self, virtual_bench, can_interface):
        """
        Check the LimpHome Pre Sleep to LimpHome transition
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        can_interface.receive_all_not_async(number_of_frames=10, frame_id=0x18FFB0F4, extended=True, timeout=20.0)
        assert can_interface.rx_frames[-1].data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
        # Go to LimpHome PreSleep
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        while rx_frame.data[1] != NMOSEK_OPCODE_LIMP_HOME_SLEEP:
            rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        # Go back to LimpHome
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
        # Go back to LimpHome
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_SLEEP_WITH_ACK_1, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True, timeout=2.0)
        assert rx_frame is None
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True, timeout=2.0)
        assert rx_frame.data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP

    def test_wait_bus_sleep_to_limp_home_pre_sleep(self, virtual_bench, can_interface):
        """
        Check the LimpHome Pre Sleep to LimpHome transition
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        can_interface.receive_all_not_async(number_of_frames=10, frame_id=0x18FFB0F4, extended=True, timeout=20.0)
        assert can_interface.rx_frames[-1].data[1] == NMOSEK_OPCODE_LIMP_HOME_NO_SLEEP
        # Go to LimpHome PreSleep
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        while rx_frame.data[1] != NMOSEK_OPCODE_LIMP_HOME_SLEEP:
            rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True, timeout=2.0)
        assert rx_frame is None
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18FFB0F4, extended=True)
        assert rx_frame.data[1] == NMOSEK_OPCODE_LIMP_HOME_SLEEP

    @staticmethod
    def __check_wait_bus_sleep_and_bus_sleep(virtual_bench, can_interface):
        """
        Check the NMWaitBusSleep and NMBusSleep transitions
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        # Check there are no new frames sent
        newFrame = can_interface.read_frame(0x18FFB0F4, extended=True, timeout=2.0)
        assert newFrame is None
        # Check power consumption is still high
        current = virtual_bench.ps_get_current_consumption(NI_8012.PS_25V_NEG)
        assert current > 0.01
        time.sleep(
            NMOSEK_TIMER_T_WBS - 2 - 0.5)  # Minus 2 because the timeout when checking no CAN frame is transmitted in sleep mode
        # Check power consumption is still high
        current = virtual_bench.ps_get_current_consumption(NI_8012.PS_25V_NEG)
        assert current > 0.01
        time.sleep(1)
        # Check that power consumption is low
        current = virtual_bench.ps_get_current_consumption(NI_8012.PS_25V_NEG)
        assert current < 0.002

    async def __wakeup_with_can_frame_and_get_frames(self, virtual_bench, can_interface, frame_id=None, number_of_frames=5, timeout=10.0):
        # Purge Rx frames
        can_interface.reset()
        print("RUN REAL TEST - CAN IS PURGED")
        await asyncio.gather(self.__wait_and_send_a_wakeup_can_frame(can_interface), can_interface.receive_all(
            extended=True,
            number_of_frames=number_of_frames,
            timeout=timeout,
            frame_id=frame_id))

    async def __wakeup_with_voltage_and_get_frames(self, virtual_bench, can_interface, frame_id=None, number_of_frames=5, timeout=10.0):
        # Purge Rx frames
        can_interface.reset()
        print("RUN REAL TEST - CAN IS PURGED")
        await asyncio.gather(self.__wait_and_set_power_supply(virtual_bench, 14.0), can_interface.receive_all(
            extended=True,
            number_of_frames=number_of_frames,
            timeout=timeout,
            frame_id=frame_id))

    async def __power_on_and_get_frames(self, virtual_bench, can_interface, frame_id=None, number_of_frames=20, timeout=20.0):
        # Purge Rx frames
        can_interface.reset()
        print("RUN REAL TEST - CAN IS PURGED")
        await asyncio.gather(self.__wait_and_power_on(virtual_bench), can_interface.receive_all(
            extended=True,
            number_of_frames=number_of_frames,
            timeout=timeout,
            frame_id=frame_id))

    @staticmethod
    async def __wait_and_send_a_wakeup_can_frame(can_interface):
        await asyncio.sleep(0.5)
        message = can.Message(is_extended_id=True, arbitration_id=NMOSEK_CAN_ID_IC,
                              data=[NMOSEK_OWN_ADDRESS, NMOSEK_OPCODE_RING_NO_SLEEP, 0, 0, 0, 0, 0, 0])
        can_interface.send_frame(message)

    async def __wait_and_set_power_supply(self, virtual_bench, voltage):
        await asyncio.sleep(0.5)
        self.__set_voltages(virtual_bench, voltage)

    @staticmethod
    async def __wait_and_power_on(virtual_bench):
        await asyncio.sleep(0.5)
        virtual_bench.ps_enable()

    @staticmethod
    def __set_voltages(virtual_bench, voltage):
        """
        Set both power supply voltages to the same value
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param voltage: voltage to be set
        :return:
        """
        virtual_bench.ps_configure_output(NI_8012.PS_25V_POS, voltage, 0.1)
        virtual_bench.ps_configure_output(NI_8012.PS_25V_NEG, -voltage, 0.1)

