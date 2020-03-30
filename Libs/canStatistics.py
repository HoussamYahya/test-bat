import can
import time
from statistics import mean, pstdev
import asyncio

CAN_INTERFACE_PEAK = 'pcan'


class canStatistics:
    """
    Class that define object to recover CAN statistics
    """

    def __init__(self, interface='pcan', channel='PCAN_USBBUS1', bitrate=500000):
        """
        Get the resource for the CAN interface
        :param interface: interface to be used
        :param channel: channel to be used
        :param bitrate: baudrate of the CAN communication
        """
        self.bus = can.interface.Bus(bustype=interface, channel=channel, bitrate=bitrate)
        self.stop_rx = False
        self.rx_frames = []

    def get_period(self, frame_id, number_of_frames, extended=False, timeout=10.0):
        """
        Get the period statistics
        :param frame_id: CAN identifier of the frame
        :param number_of_frames: number of frames to get to calculate the statistics
        :param extended: True if the CAN identifier is in extended format (29-bits long)
        :param timeout: maximum time (s) to get the frames
        :return: statistics on periods
        """
        print(f"CALL get_period, frame_id={frame_id}, number_of_frames={number_of_frames}, extended={extended}, timeout={timeout}")
        self.bus.set_filters(filters=[{"can_id": frame_id, "can_mask": 0x1FFFFFFF, "extended": extended}])
        time_end = time.time() + timeout
        countedRxFrames = -1
        frames = []
        # Get the frames
        while time.time() < time_end and countedRxFrames < number_of_frames:
            msgRx = self.bus.recv(timeout)
            if msgRx is not None:
                countedRxFrames += 1
                frames.append(msgRx.timestamp)
        # If there are at least 2 frames, estimate the statistics
        if len(frames) > 1:
            # Remove the first frame, otherwise period is miss calculated
            frames = frames[1:]
            periods = [j - i for i, j in zip(frames[:-1], frames[1:])]
            self.bus.set_filters(filters=None)
            return statistic_object(periods)
        else:
            return None

    async def receive_all(self, number_of_frames=50, frame_id=None, extended=False, timeout=10.0):
        """
        Receive all frames in an asynchronous way
        :param number_of_frames: number of frames to get
        :param frame_id: CAN identifier of the frame to receive. Set to None to receive all frames
        :param extended: True if the CAN identifier is in extended format (29-bits long)
        :param timeout: maximum time (s) to get the frames
        :return: All frames received
        """
        print(f"CALL receive_all, frame_id={frame_id}, number_of_frames={number_of_frames}, extended={extended}, timeout={timeout}")

        self.rx_frames = []
        countedRxFrames = 0
        time_end = time.time() + timeout
        if frame_id is not None:
            self.bus.set_filters(filters=[{"can_id": frame_id, "can_mask": 0x1FFFFFFF, "extended": extended}])
        else:
            self.bus.set_filters(filters=[{"can_id": 0, "can_mask": 0x00000000, "extended": extended}])
        # Get all messages
        while time.time() < time_end and countedRxFrames < number_of_frames:
            await asyncio.sleep(0.01)
            msgRx = self.bus.recv(timeout/10)
            if msgRx is not None:
                self.rx_frames.append(msgRx)
                print(msgRx)
            else:
                print("no rx")


class statistic_object:
    min_value = None
    max_value = None
    mean_value = None
    stdev_value = None
    number_of_values = None

    def __init__(self, list_of_data):
        """
        Get statistics out of the input parameters
        :param list_of_data: list of the data to be recovered
        :return: None
        """
        if len(list_of_data) > 0:
            self.max_value = max(list_of_data)
            self.min_value = min(list_of_data)
            self.mean_value = mean(list_of_data)
            self.stdev_value = pstdev(list_of_data)
            self.number_of_values = len(list_of_data)

    def __str__(self):
        """
        :return: string for print function
        """
        return (f"MAX   : {self.max_value}\n"
                f"MIN   : {self.min_value}\n"
                f"MEAN  : {self.mean_value}\n"
                f"STDEV : {self.stdev_value}\n"
                f"COUNT : {self.number_of_values}")

