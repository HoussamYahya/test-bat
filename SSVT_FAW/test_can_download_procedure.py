import Libs.NI_8012 as NI_8012
from pytest import mark
import time
import can

@mark.can_download_procedure
def test_download_sequence(virtual_bench, can_interface):
    """
    Validate the start of the download procedure
    :param virtual_bench: fixture of pytest to use the NI virtual bench
    :param can_interface: fixture of pytest to use CAN interface
    :return:
    """
    virtual_bench.ps_configure_output(NI_8012.PS_25V_POS, 13.0, 0.1)
    virtual_bench.ps_configure_output(NI_8012.PS_25V_NEG, -13.0, 0.1)
    virtual_bench.ps_generate_por()
    # Send the go to extended session request
    message = can.Message(is_extended_id=True, arbitration_id=0x18DB33F1,
                            data=[0x02, 0x10, 0x03, 0, 0, 0, 0, 0])
    can_interface.send_frame(message)
    can_interface.reset()
    # check the are no response
    rx_frame = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
    assert rx_frame is None
    # Send a Control DTC request
    message = can.Message(is_extended_id=True, arbitration_id=0x18DB33F1,
                            data=[0x02, 0x85, 0x02, 0, 0, 0, 0, 0])
    can_interface.send_frame(message)
    can_interface.reset()
    # check the are no response
    rx_frame = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
    assert rx_frame is None
    # Send a Communication control request
    rx_frame = can_interface.read_frame(None, extended=True)
    assert rx_frame is not None
    message = can.Message(is_extended_id=True, arbitration_id=0x18DB33F1,
                            data=[0x03, 0x28, 0x03, 0x03, 0, 0, 0, 0])
    can_interface.send_frame(message)
    can_interface.reset()
    # check the are no response
    rx_frame = can_interface.read_frame(0x18DAF1F4, extended=True, timeout=1.0)
    assert rx_frame is None
    # check frames are stopped
    rx_frame = can_interface.read_frame(None, extended=True, timeout=1.0)
    assert rx_frame is None
    # Send a ECU reset request
    message = can.Message(is_extended_id=True, arbitration_id=0x18DB33F1,
                            data=[0x02, 0x11, 0x01, 0, 0, 0, 0, 0])
    can_interface.send_frame(message)
    can_interface.reset()
    # check first frame sent is a NMOSEK frame
    rx_frame = can_interface.read_frame(None, extended=True)
    assert rx_frame.arbitration_id == 0x18FFB0F4


