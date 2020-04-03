import Libs.NI_8012 as NI_8012
from pytest import mark
import time

FRAME_COUNT_TO_GET = 10

# Parameters based on FAW_J6_IBS_CANMatrix V1.0 2019-01-28
@mark.parametrize(
    ("frame_id",        "expected_period"), [
        (0x18FC0AF4,    0.1),
        (0x18FC09F4,    1),
        (0x18FC08F4,    0.1),
        (0x18FC07F4,    1),
        (0x18FF4FF4,    0.1),
        (0x18FF4EF4,    0.1),
        (0x18FF4DF4,    1),
        (0x18FECAF4,    1)
])
@mark.can_frame_periods
class Test_can_periods:
    def test_periods_after_reset(self, virtual_bench, can_interface, frame_id, expected_period):
        """
        Validate the periods of the CAN frames after reset of the sensor
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :param frame_id: frame identifier as parametrize of pytest
        :param expected_period: period od the frame as parametrize of pytest
        :return:
        """
        self.__set_voltages(virtual_bench, 13.0)
        virtual_bench.ps_generate_por()
        rx_stats = can_interface.get_period(frame_id, FRAME_COUNT_TO_GET, extended=True, timeout=FRAME_COUNT_TO_GET*expected_period)
        self.__check_periods(rx_stats, expected_period)

    def test_periods_after_wakeup_with_voltage(self, virtual_bench, can_interface, frame_id, expected_period):
        """
        Validate the periods of the CAN frames after reset of the sensor
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :param frame_id: frame identifier as parametrize of pytest
        :param expected_period: period od the frame as parametrize of pytest
        :return:
        """
        self.__set_voltages(virtual_bench, 11.0)
        virtual_bench.ps_generate_por()
        time.sleep(70)
        can_interface.reset()
        self.__set_voltages(virtual_bench, 14.0)
        rx_stats = can_interface.get_period(frame_id, FRAME_COUNT_TO_GET, extended=True, timeout=FRAME_COUNT_TO_GET*expected_period)
        self.__check_periods(rx_stats, expected_period)

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

    @staticmethod
    def __check_periods(rx_stats, expected_period):
        """
        Assert the measured period statistics (min, max and mean values)
        :param rx_stats: statistics of the measured periods
        :param expected_period: expected period duration
        :return:
        """
        assert rx_stats.min_value > 0.9*expected_period
        assert rx_stats.max_value < 1.1*expected_period
        assert 0.99 * expected_period < rx_stats.mean_value < 1.01 * expected_period
