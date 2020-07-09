import Libs.NI_8012 as NI_8012
from pytest import mark
import time
import can


@mark.production_issues
def test_get_xde20_routine_results_with_stmin_5ms(can_interface):#(virtual_bench, can_interface):
    """
    Check that the stmin 5ms works properly
    :param virtual_bench: fixture of pytest to use the NI virtual bench
    :param can_interface: fixture of pytest to use CAN interface
    :return:
    """
    #virtual_bench.ps_configure_output(NI_8012.PS_25V_POS, 13.0, 0.1)
    #virtual_bench.ps_configure_output(NI_8012.PS_25V_NEG, -13.0, 0.1)
    #virtual_bench.ps_generate_por()
    time.sleep(0.2)
    # Send the go to calibration session request
    message = can.Message(is_extended_id=True, arbitration_id=0x18DAF4F1,
                          data=[0x02, 0x10, 0x60, 0, 0, 0, 0, 0])
    can_interface.send_frame(message)
    rx_frame = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
    assert list(rx_frame.data[0:3]) == [0x02, 0x50, 0x60]
    # Request the seed
    message.data = [0x02, 0x27, 0x01, 0, 0, 0, 0, 0]
    can_interface.send_frame(message)
    rx_frame = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
    assert list(rx_frame.data[0:3]) == [0x06, 0x67, 0x01]
    # Send the key
    seed = rx_frame.data[3:7]
    print(f'SEED : {seed}')
    crc16_result = crc16(seed, 0, 4)
    crc = (crc16_result * 65536 + crc16_result) ^ 0x5A5AC3C3
    crc = crc.to_bytes(4, 'big')
    print(f'KEY : {crc}')
    message.data = [0x06, 0x27, 0x02, crc[0], crc[1], crc[2], crc[3], 0]
    can_interface.send_frame(message)
    rx_frame = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
    assert list(rx_frame.data[0:3]) == [0x02, 0x67, 0x02]
    # Send communication control request
    message_cc = can.Message(is_extended_id=True, arbitration_id=0x18DB33F1,
                            data=[0x03, 0x28, 0x03, 0x03, 0, 0, 0, 0])
    can_interface.send_frame(message_cc)
    # check the are no response
    rx_frame = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
    assert rx_frame is None
    # check frames are stopped
    can_interface.reset()
    rx_frame = can_interface.read_frame(None, extended=True, timeout=1.0)
    assert rx_frame is None
    for i in range(5):
        # Start routine DE20 with filtering time of 100ms
        message.data = [0x06, 0x31, 0x01, 0xDE, 0x20, 0, 100, 0]
        can_interface.send_frame(message)
        rx_frame = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
        assert list(rx_frame.data[0:5]) == [0x04, 0x71, 0x01, 0xDE, 0x20]
        # Get the results
        message_sf = can.Message(is_extended_id=True, arbitration_id=0x18DAF4F1,
                              data=[0x06, 0x31, 0x03, 0xDE, 0x20, 0, 100, 0])
        message_fc = can.Message(is_extended_id=True, arbitration_id=0x18DAF4F1,
                              data=[0x30, 0, 5, 0, 0, 0, 0, 0])
        time.sleep(0.35)
        can_interface.send_frame(message_sf)
        rx_frame_ff = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
        can_interface.send_frame(message_fc)
        rx_frame_cf = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
        assert list(rx_frame_ff.data[0:6]) == [0x10, 0x0A, 0x71, 0x03, 0xDE, 0x20]
        assert list(rx_frame_cf.data[0:1]) == [0x21]
        can_interface.reset()
        #for j in range (100):
        #    can_interface.read_frame(None, extended=True, timeout=1.0)


def crc16(data: bytearray, offset, length):
    if data is None or offset < 0 or offset > len(data) - 1 and offset+length > len(data):
        return 0
    crc = 0xFFFF
    for i in range(0, length):
        crc ^= data[offset + i] << 8
        for j in range(0, 8):
            if (crc & 0x8000) > 0:
                crc =(crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF
