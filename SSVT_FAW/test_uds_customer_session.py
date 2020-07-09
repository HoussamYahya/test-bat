import Libs.NI_8012 as NI_8012
import can
from pytest import mark
import time

did_list_read = [0x82, 0x87, 0x8C, 0x90, 0x92, 0x93, 0x94, 0x95, 0x98, 0x99, 0x9D, 0xA0, 0xA1]
did_list_size = [16,   16,   16,   17,   16,   16,   16,   16,   10,   4,    4,    16,     16]
did_list_read_write_in_customer_session = [0x90, 0x98, 0x99, 0x9D, 0xA0, 0xA1]


@mark.uds_customer
class TestUdsCustomer:
    def test_go_to_customer_session(self, virtual_bench, can_interface):
        """
        Validate that we can go into customer session, and that seed/key exchange is OK
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        power_on_sensor(virtual_bench, 13.0)
        go_to_customer_session_and_unlock(can_interface)

    @mark.parametrize("did", did_list_read)
    def test_read_access_to_customer_did_f1(self, virtual_bench, can_interface, did):
        """
        Check that the customer has read access to the 0xF1xx DIDs
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        power_on_sensor(virtual_bench, 13.0)
        go_to_customer_session_and_unlock(can_interface)
        rx_frame = send_tp_data(can_interface, [0x22, 0xF1, did])
        if rx_frame.data[0] & 0xF0 == 0x10:
            assert rx_frame.data[2] == 0x62
            assert rx_frame.data[1] == did_list_size[did_list_read.index(did)] + 3
        else:
            assert rx_frame.data[1] == 0x62
            assert rx_frame.data[0] == did_list_size[did_list_read.index(did)] + 3

    @mark.parametrize("did", did_list_read)
    def test_write_access_to_customer_did_f1(self, virtual_bench, can_interface, did):
        """
        Check that the customer has read access to the 0xF1xx DIDs
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        power_on_sensor(virtual_bench, 13.0)
        go_to_customer_session_and_unlock(can_interface)
        size = did_list_size[did_list_read.index(did)]
        rx_frame = send_tp_data(can_interface, [0x2E, 0xF1, did] + [0x55] * size)
        if did in did_list_read_write_in_customer_session:
            assert rx_frame.data[1] == 0x6E
        else:
            assert rx_frame.data[1] == 0x7F

    def test_write_and_read_did_0x0100(self, virtual_bench, can_interface):
        """
        Check that the customer has read access to the 0xF1xx DIDs
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param can_interface: fixture of pytest to use CAN interface
        :return:
        """
        power_on_sensor(virtual_bench, 13.0)
        go_to_customer_session_and_unlock(can_interface)
        rx_frame = send_tp_data(can_interface, [0x22, 0x01, 0x00])
        assert rx_frame.data[2] == 0x62
        power_on_sensor(virtual_bench, 13.0)
        go_to_customer_session_and_unlock(can_interface)
        rx_frame = send_tp_data(can_interface, [0x2E, 0x01, 0x00] + [0x55] * 16)
        assert rx_frame.data[1] == 0x6E

    # Todo : test did 0x0b..


def send_tp_data(can_interface, data):
    if len(data) <= 7:
        rx_frame = send_tp_sf(can_interface, data)
    else:
        rx_frame = send_tp_ff_cf(can_interface, data)
    return rx_frame


def send_tp_sf(can_interface, data):
    tx_data = [len(data)] + data + [0]*(7-len(data))
    message = can.Message(is_extended_id=True, arbitration_id=0x18DAF4F1,
                          data=tx_data)
    can_interface.send_frame(message)
    can_interface.reset()
    rx_frame = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
    return rx_frame


def send_tp_ff_cf(can_interface, data):
    tx_data = [0x10, len(data)] + data[:6]
    remaining_size = len(data) - 6
    next_data_start_index = 6
    cf_index = 0x21
    message = can.Message(is_extended_id=True, arbitration_id=0x18DAF4F1,
                          data=tx_data)
    can_interface.send_frame(message)
    can_interface.reset()
    rx_frame = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
    while remaining_size > 0:
        if remaining_size >= 7:
            message.data = [cf_index] + data[next_data_start_index:next_data_start_index+7]
        else:
            message.data = [cf_index] + data[next_data_start_index:] + [0]*(7-remaining_size)
        time.sleep(0.01)
        can_interface.send_frame(message)
        remaining_size -= 7
        next_data_start_index += 7
        cf_index += 1
    can_interface.reset()
    rx_frame = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
    return rx_frame


def go_to_customer_session_and_unlock(can_interface):
    # Send the DSC UDS request and check the response
    rx_frame = send_tp_data(can_interface, [0x10, 0x63])
    assert list(rx_frame.data[0:3]) == [0x02, 0x50, 0x63]
    # Request the seed
    rx_frame = send_tp_data(can_interface, [0x27, 0x01])
    assert list(rx_frame.data[0:3]) == [0x06, 0x67, 0x01]
    # Send the key
    seed = (rx_frame.data[3] << 24) + (rx_frame.data[4] << 16) + (rx_frame.data[5] << 8) + rx_frame.data[6]
    key = compute_faw_key(seed)
    rx_frame = send_tp_data(can_interface, [0x27, 0x02, key >> 24, (key >> 16) & 0xFF, (key >> 8) & 0xFF, key & 0xFF])
    assert list(rx_frame.data[0:3]) == [0x02, 0x67, 0x02]


def power_on_sensor(virtual_bench, voltage):
    virtual_bench.ps_configure_output(NI_8012.PS_25V_POS, voltage, 0.1)
    virtual_bench.ps_configure_output(NI_8012.PS_25V_NEG, -voltage, 0.1)
    virtual_bench.ps_generate_por()


def compute_faw_key(seed):
    key = seed

    if 0x00000000 != (key & 0xFFFF0000):
        for i in range(35):
            if key & 0x80000000:
                key <<= 1
                key ^= 0x4288397E
            else:
                key <<= 1
            key &= 0xFFFFFFFF

    return key
