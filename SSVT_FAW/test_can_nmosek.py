import Libs.NI_8012 as NI_8012
from pytest import mark
import time
import asyncio


@mark.can_nmosek
class Test_can_nmosek:
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

    def test_get_first_frames(self, virtual_bench, can_interface):
        self.__set_voltages(virtual_bench, 13.0)
        virtual_bench.ps_disable()
        asyncio.run(self.__power_on_and_get_frames(virtual_bench, can_interface))
        print(len(can_interface.rx_frames))

    async def __power_on_and_get_frames(self, virtual_bench, can_interface):
        await asyncio.gather(self.__wait_and_power_on(virtual_bench), can_interface.receive_all(extended=True, frame_id=0x18FFB0F4))

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
