#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import traceback
import time
from ctypes import *

import PLinApi


class Lin_Peak_For_Volvo(object):
    """
    """
    breadLinMessage = True
    linStatus = False
    FRAME_FILTER_MASK = c_uint64(0xFFFFFFFFFFFFFFFF)

    GLOBAL_FRAME_TABLE = {
        0x00: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x01: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x02: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x03: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x04: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x05: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x06: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x07: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x08: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x09: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x0A: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x0B: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x0C: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x0D: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x0E: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x0F: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},

        0x10: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x11: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x12: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x13: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x14: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x15: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x16: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x17: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x18: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x19: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x1A: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x1B: {"dir": PLinApi.TLIN_DIRECTION_SUBSCRIBER, "cst": PLinApi.TLIN_CHECKSUMTYPE_ENHANCED, "len": 7},
        0x1C: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x1D: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x1E: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},
        0x1F: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},

        0x20: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 2},

        0x21: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x22: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x23: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x24: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x25: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x26: {"dir": PLinApi.TLIN_DIRECTION_SUBSCRIBER, "cst": PLinApi.TLIN_CHECKSUMTYPE_ENHANCED, "len": 8},
        0x27: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x28: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x29: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},

        0x2A: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},

        0x2B: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},
        0x2C: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x2D: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x2E: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x2F: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x30: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x31: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 4},
        0x32: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 1},
        0x33: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 1},
        0x34: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},
        0x35: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},
        0x36: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},
        0x37: {"dir": PLinApi.TLIN_DIRECTION_PUBLISHER, "cst": PLinApi.TLIN_CHECKSUMTYPE_ENHANCED, "len": 8},
        0x38: {"dir": PLinApi.TLIN_DIRECTION_PUBLISHER, "cst": PLinApi.TLIN_CHECKSUMTYPE_ENHANCED, "len": 2},
        0x39: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},
        0x3A: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},
        0x3B: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},
        0x3C: {"dir": PLinApi.TLIN_DIRECTION_PUBLISHER, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},
        0x3D: {"dir": PLinApi.TLIN_DIRECTION_SUBSCRIBER, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},
        0x3E: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},
        0x3F: {"dir": PLinApi.TLIN_DIRECTION_DISABLED, "cst": PLinApi.TLIN_CHECKSUMTYPE_CLASSIC, "len": 8},
    }

    # frame for BWC
    MasterReq_SlaveResp_Table0 = [
        {"id": [0x38], "delay": 10, "type": PLinApi.TLIN_SLOTTYPE_UNCONDITIONAL},
        {"id": [0x1B], "delay": 20, "type": PLinApi.TLIN_SLOTTYPE_UNCONDITIONAL},
        {"id": [0x26], "delay": 10, "type": PLinApi.TLIN_SLOTTYPE_UNCONDITIONAL},
        {"id": [0x3C], "delay": 20, "type": PLinApi.TLIN_SLOTTYPE_MASTER_REQUEST},
        {"id": [0x3D], "delay": 20, "type": PLinApi.TLIN_SLOTTYPE_SLAVE_RESPONSE},
    ]
    
    # Frame for Bats 2
    MasterReq_SlaveResp_Table2 = [
        {"id": [0x38], "delay": 10, "type": PLinApi.TLIN_SLOTTYPE_UNCONDITIONAL},
        {"id": [0x1B], "delay": 20, "type": PLinApi.TLIN_SLOTTYPE_UNCONDITIONAL},
        {"id": [0x26], "delay": 10, "type": PLinApi.TLIN_SLOTTYPE_UNCONDITIONAL},
        {"id": [0x3C], "delay": 20, "type": PLinApi.TLIN_SLOTTYPE_MASTER_REQUEST},
        {"id": [0x3D], "delay": 20, "type": PLinApi.TLIN_SLOTTYPE_SLAVE_RESPONSE},
    ]

    def __init__(self):
        """
        """
        self.m_objPLinApi = PLinApi.PLinApi()
        self.m_hClient = PLinApi.HLINCLIENT(0)
        self.m_hHw = PLinApi.HLINHW(0)
        self.m_HwMode = PLinApi.TLIN_HARDWAREMODE_MASTER
        self.m_HwBaudrate = c_ushort(9600)
        self.m_lMask = self.FRAME_FILTER_MASK
        # initialize a dictionnary to get LIN ID from PID
        self.PIDs = {}
        for i in range(64):
            nPID = c_ubyte(i)
            self.m_objPLinApi.GetPID(nPID)
            self.PIDs[nPID.value] = i        

        if not self.m_objPLinApi.isLoaded():
            raise Exception("PLin-API could not be loaded ! Exiting...")

    def connect(self, name, device_number, channel_number):
        """
        :param name:
        :param device_number:
        :param channel_number:
        :return:
        """
        if self.m_objPLinApi.RegisterClient(name, None, self.m_hClient) != PLinApi.TLIN_ERROR_OK:
            raise Exception("Connect Failed")

        self.m_objPLinApi.ResetClient(self.m_hClient)

        self.m_hHw = PLinApi.HLINHW(device_number)

        if self.m_objPLinApi.ConnectClient(self.m_hClient, self.m_hHw) != PLinApi.TLIN_ERROR_OK:
            raise Exception("Connect Failed")

        mode = c_int(0)
        baudrate = c_int(0)

        if self.m_objPLinApi.GetHardwareParam(
                self.m_hHw, PLinApi.TLIN_HARDWAREPARAM_MODE, mode, 0) != PLinApi.TLIN_ERROR_OK:
            raise Exception("Connect Failed")
        if self.m_objPLinApi.GetHardwareParam(
                self.m_hHw, PLinApi.TLIN_HARDWAREPARAM_BAUDRATE, baudrate, 0) != PLinApi.TLIN_ERROR_OK:
            raise Exception("Connect Failed")

        self.m_objPLinApi.ResetHardware(self.m_hClient, self.m_hHw)

        if mode.value == PLinApi.TLIN_HARDWAREMODE_NONE.value or baudrate.value != self.m_HwBaudrate.value:
            if self.m_objPLinApi.InitializeHardware(
                    self.m_hClient, self.m_hHw, self.m_HwMode, self.m_HwBaudrate) != PLinApi.TLIN_ERROR_OK:
                raise Exception("Connect Failed")
            if self.m_objPLinApi.SetClientFilter(
                    self.m_hClient, self.m_hHw, self.m_lMask) != PLinApi.TLIN_ERROR_OK:
                raise Exception("Connect Failed")

    def disconnect(self):
        """
        :return:
        """

        if self.m_objPLinApi.DisconnectClient(self.m_hClient, self.m_hHw) == PLinApi.TLIN_ERROR_OK:
            self.m_hHw = PLinApi.HLINHW(0)
            self.m_objPLinApi.RemoveClient(self.m_hClient)

    def set_frame_entry(self, frameId, direction, cst, length):
        """
        :param frameId:
        :param direction:
        :param cst:
        :param length:
        :return:
        """
        frame_entry = PLinApi.TLINFrameEntry()
        frame_entry.FrameId = c_ubyte(frameId)
        frame_entry.ChecksumType = cst
        frame_entry.Direction = direction
        frame_entry.Length = c_ubyte(length)
        frame_entry.Flags = PLinApi.FRAME_FLAG_RESPONSE_ENABLE

        if self.m_objPLinApi.SetFrameEntry(self.m_hClient, self.m_hHw, frame_entry) == PLinApi.TLIN_ERROR_OK:
            mask = c_uint64(1 << frameId)
            self.m_lMask = c_uint64(self.m_lMask.value | mask.value)
            if self.m_objPLinApi.SetClientFilter(self.m_hClient, self.m_hHw, self.m_lMask) != PLinApi.TLIN_ERROR_OK:
                raise Exception("Connect Failed")

    def set_global_frame_table(self):
        """
        :return:
        """
        for frame_id in self.GLOBAL_FRAME_TABLE:
            entry = self.GLOBAL_FRAME_TABLE[frame_id]
            self.set_frame_entry(
                frameId=frame_id, direction=entry['dir'], cst=entry['cst'], length=entry['len'])

    def get_global_frame_table(self):
        """
        :return:
        """

        table = {}

        self.m_lMask = c_uint64(0x0)
        mask = c_uint64(0x0)

        for index in range(64):
            frame_entry = PLinApi.TLINFrameEntry()
            frame_entry.FrameId = c_ubyte(index)
            frame_entry.ChecksumType = PLinApi.TLIN_CHECKSUMTYPE_AUTO
            frame_entry.Direction = PLinApi.TLIN_DIRECTION_SUBSCRIBER_AUTOLENGTH

            if (index >= 0x00) and (index <= 0x1F):
                frame_entry.Length = c_ubyte(2)
            elif (index >= 0x20) and (index <= 0x2F):
                frame_entry.Length = c_ubyte(4)
            elif (index >= 0x30) and (index <= 0x3F):
                frame_entry.Length = c_ubyte(8)

            if self.m_objPLinApi.GetFrameEntry(self.m_hHw, frame_entry) == PLinApi.TLIN_ERROR_OK:

                table[frame_entry.FrameId] = {
                    "dir": frame_entry.Direction,
                    "cst": frame_entry.ChecksumType,
                    "len": frame_entry.Length
                }

                if frame_entry.Direction != PLinApi.TLIN_DIRECTION_DISABLED.value:
                    mask = c_uint64((1 << index) & self.FRAME_FILTER_MASK.value)
                    self.m_lMask = c_uint64(self.m_lMask.value | mask.value)

            if (self.m_hClient.value != 0) and (self.m_hHw.value != 0):
                self.m_objPLinApi.SetClientFilter(self.m_hClient, self.m_hHw, self.m_lMask)

        for cle,valuers in table.items():
            print(cle, valuers)

        return table

    def set_schedule_table(self, table_id):
        """
        :param table_id:
        :return:
        """
        schedule_slot_array = (PLinApi.TLINScheduleSlot * len(self.MasterReq_SlaveResp_Table0))
        schedule_table = schedule_slot_array()

        for index, entry in enumerate(self.MasterReq_SlaveResp_Table0):
            schedule_entry = PLinApi.TLINScheduleSlot()

            for pos, frameId in enumerate(entry["id"]):
                schedule_entry.FrameId[pos] = c_ubyte(frameId)
            schedule_entry.Type = entry["type"]
            schedule_entry.Delay = c_ushort(entry["delay"])
            schedule_entry.CountResolve = c_ubyte(0)

            schedule_table[index] = schedule_entry

        self.m_objPLinApi.SetSchedule(self.m_hClient, self.m_hHw, table_id, schedule_table, len(self.MasterReq_SlaveResp_Table0))

    def get_schedule_table(self, table_id):
        """
        :param table_id:
        :return:
        """
        schedule_slot_array = (PLinApi.TLINScheduleSlot * 256)
        schedule_table = schedule_slot_array()

        count = c_int(0)
        self.m_objPLinApi.GetSchedule(self.m_hHw, table_id, schedule_table, c_int(256), count)

        for index in range(count.value):
            schedule_entry = schedule_table[index]
            print(
                schedule_entry.Type,
                schedule_entry.Delay,
                schedule_entry.FrameId[0],
                schedule_entry.CountResolve,
                schedule_entry.Handle
            )

    def delete_schedule_table(self, table_id):
        """
        :param table_id:
        :return:
        """
        self.m_objPLinApi.DeleteSchedule(self.m_hClient, self.m_hHw, table_id)

    def start_schedule_table(self, table_id):
        """
        :param table_id:
        :return:
        """
        self.m_objPLinApi.StartSchedule(self.m_hClient, self.m_hHw, table_id)

    def resume_schedule_table(self):
        """
        :return:
        """
        self.m_objPLinApi.ResumeSchedule(self.m_hClient, self.m_hHw)

    def suspend_schedule_table(self):
        """
        :return:
        """
        self.m_objPLinApi.SuspendSchedule(self.m_hClient, self.m_hHw)

    def update_schedule_data(self, frame_id, data=[]):
        """
        :param frame_id:
        :param data:
        :return:
        """

        raw_data = (c_ubyte * len(data))()
        for index, byte in enumerate(data):
            raw_data[index] = c_ubyte(byte)

        self.m_objPLinApi.UpdateByteArray(self.m_hClient, self.m_hHw, c_ubyte(frame_id), 0, c_ubyte(len(data)),
                                          raw_data)

    def write_frame(self, frame_id, data=[]):
        """
        :param frame_id:
        :param data:
        :return:
        """

        frame_entry = PLinApi.TLINFrameEntry()
        frame_entry.FrameId = c_ubyte(frame_id)
        self.m_objPLinApi.GetFrameEntry(self.m_hHw, frame_entry)

        msg = PLinApi.TLINMsg()
        msg.Direction = PLinApi.TLINDirection(frame_entry.Direction)
        msg.ChecksumType = PLinApi.TLINChecksumType(frame_entry.ChecksumType)
        msg.Length = c_ubyte(frame_entry.Length)

        for index in range(frame_entry.Length):
            msg.Data[index] = c_ubyte(data[index])

        private_id = c_ubyte(frame_id)
        self.m_objPLinApi.GetPID(private_id)
        msg.FrameId = c_ubyte(private_id.value)
        self.m_objPLinApi.CalculateChecksum(msg)
        self.m_objPLinApi.Write(self.m_hClient, self.m_hHw, msg)

    def getFormattedRcvMsg(self, msg):
        """
        Returns a string formatted LIN receive message

        Parameters:
            msg a Lin receive message (TLINRcvMsg)

        Returns:
            a string formatted LIN message
        """
        # Check if the received frame is a standard type.
        # If it is not a standard type then ignore it.
        if (msg.Type != PLinApi.TLIN_MSGTYPE_STANDARD.value):
            if (msg.Type == PLinApi.TLIN_MSGTYPE_BUS_SLEEP.value):
                strTemp = 'Bus Sleep status message'
            elif (msg.Type == PLinApi.TLIN_MSGTYPE_BUS_WAKEUP.value):
                strTemp = 'Bus WakeUp status message'
            elif (msg.Type == PLinApi.TLIN_MSGTYPE_AUTOBAUDRATE_TIMEOUT.value):
                strTemp = 'Auto-baudrate Timeout status message'
            elif (msg.Type == PLinApi.TLIN_MSGTYPE_AUTOBAUDRATE_REPLY.value):
                strTemp = 'Auto-baudrate Reply status message'
            elif (msg.Type == PLinApi.TLIN_MSGTYPE_OVERRUN.value):
                strTemp = 'Bus Overrun status message'
            elif (msg.Type == PLinApi.TLIN_MSGTYPE_QUEUE_OVERRUN.value):
                strTemp = 'Queue Overrun status message'
            else:
                strTemp = 'Non standard message'
            return strTemp
        # format Data field as string
        dataStr = ""
        for i in range(msg.Length):
            dataStr = str.format("{0}{1} ", dataStr,  hex(msg.Data[i]))
        # remove ending space
        dataStr = dataStr[:-1]
        # format Error field as string
        error = ""
        if (msg.ErrorFlags & PLinApi.TLIN_MSGERROR_CHECKSUM):
            error = error + 'Checksum,'
        if (msg.ErrorFlags & PLinApi.TLIN_MSGERROR_GROUND_SHORT):
            error = error + 'GroundShort,'
        if (msg.ErrorFlags & PLinApi.TLIN_MSGERROR_ID_PARITY_BIT_0):
            error = error + 'IdParityBit0,'
        if (msg.ErrorFlags & PLinApi.TLIN_MSGERROR_ID_PARITY_BIT_1):
            error = error + 'IdParityBit1,'
        if (msg.ErrorFlags & PLinApi.TLIN_MSGERROR_INCONSISTENT_SYNCH):
            error = error + 'InconsistentSynch,'
        if (msg.ErrorFlags & PLinApi.TLIN_MSGERROR_OTHER_RESPONSE):
            error = error + 'OtherResponse,'
        if (msg.ErrorFlags & PLinApi.TLIN_MSGERROR_SLAVE_NOT_RESPONDING):
            error = error + 'SlaveNotResponding,'
        if (msg.ErrorFlags & PLinApi.TLIN_MSGERROR_SLOT_DELAY):
            error = error + 'SlotDelay,'
        if (msg.ErrorFlags & PLinApi.TLIN_MSGERROR_TIMEOUT):
            error = error + 'Timeout,'
        if (msg.ErrorFlags & PLinApi.TLIN_MSGERROR_VBAT_SHORT):
            error = error + 'VBatShort,'
        if (msg.ErrorFlags == 0):
            error = 'O.k. '
        # remove ending comma
        error = error[:-1]
        # format message
        return([hex(self.PIDs[msg.FrameId]),
                           msg.Length,
                           dataStr,
                           msg.TimeStamp,
                           self.getFrameDirectionAsString(msg.Direction),
                           error]
                           )
                           

    # Returns the string name of a PLinApi.TLINDirection value
    #
    def getFrameDirectionAsString(self, direction):
        """
        Returns the string name of a PLinApi.TLINDirection value

        Parameters:
            value   a PLinApi.TLINDirection value (or a number)

        Returns:
            a string name of the direction value
        """
        # check given parameter
        if (isinstance(direction, PLinApi.TLINDirection)):
            value = direction.value
        else:
            value = int(direction)
        # translate value to string
        if (value == PLinApi.TLIN_DIRECTION_DISABLED.value):
            return 'Disabled'
        elif (value == PLinApi.TLIN_DIRECTION_PUBLISHER.value):
            return 'Publisher'
        elif (value == PLinApi.TLIN_DIRECTION_SUBSCRIBER.value):
            return 'Subscriber'
        elif (value == PLinApi.TLIN_DIRECTION_SUBSCRIBER_AUTOLENGTH.value):
            return 'Subscriber Automatic Length'

    # Returns the string name of a PLinApi.TLINChecksumType value
    

    def read(self,count):
        """
        :return:
        """
        self.linStatus= False
        msg_buffer = {}
        
        #while self.breadLinMessage:
        for i in range(count):    
            msg = PLinApi.TLINRcvMsg()
            if self.m_objPLinApi.Read(self.m_hClient, msg) == PLinApi.TLIN_ERROR_OK:
                self.listMsg.append(self.getFormattedRcvMsg(msg))
                self.linStatus = True
                delta = ((msg.TimeStamp - msg_buffer.setdefault(msg.FrameId, msg.TimeStamp)) / 1000.0)
                msg_buffer[msg.FrameId] = msg.TimeStamp
                '''
                if msg.Length == 1:
                    print("{} ({:>14}) : 0x{:02X} {} - {:02X} [{}]".format(
                        msg.TimeStamp, delta, msg.FrameId, msg.Length,
                        msg.Data[0], msg.ErrorFlags)
                    )
                elif msg.Length == 2:
                    print("{} ({:>14}) : 0x{:02X} {} - {:02X} {:02X} [{}]".format(
                        msg.TimeStamp, delta, msg.FrameId, msg.Length,
                        msg.Data[0],
                        msg.Data[1], msg.ErrorFlags)
                    )
                elif msg.Length == 3:
                    print("{} ({:>14}) : 0x{:02X} {} - {:02X} {:02X} {:02X} [{}]".format(
                        msg.TimeStamp, delta, msg.FrameId, msg.Length,
                        msg.Data[0],
                        msg.Data[1],
                        msg.Data[2], msg.ErrorFlags)
                    )
                elif msg.Length == 4:
                    print("{} ({:>14}) : 0x{:02X} {} - {:02X} {:02X} {:02X} {:02X} [{}]".format(
                        msg.TimeStamp, delta, msg.FrameId, msg.Length,
                        msg.Data[0],
                        msg.Data[1],
                        msg.Data[2],
                        msg.Data[3], msg.ErrorFlags)
                    )
                elif msg.Length == 5:
                    print("{} ({:>14}) : 0x{:02X} {} - {:02X} {:02X} {:02X} {:02X} {:02X} [{}]".format(
                        msg.TimeStamp, delta, msg.FrameId, msg.Length,
                        msg.Data[0],
                        msg.Data[1],
                        msg.Data[2],
                        msg.Data[3],
                        msg.Data[4], msg.ErrorFlags)
                    )
                elif msg.Length == 6:
                    print("{} ({:>14}) : 0x{:02X} {} - {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} [{}]".format(
                        msg.TimeStamp, delta, msg.FrameId, msg.Length,
                        msg.Data[0],
                        msg.Data[1],
                        msg.Data[2],
                        msg.Data[3],
                        msg.Data[4],
                        msg.Data[5], msg.ErrorFlags)
                    )
                elif msg.Length == 7:
                    print("{} ({:>14}) : 0x{:02X} {} - {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} [{}]".format(
                        msg.TimeStamp, delta, msg.FrameId, msg.Length,
                        msg.Data[0],
                        msg.Data[1],
                        msg.Data[2],
                        msg.Data[3],
                        msg.Data[4],
                        msg.Data[5],
                        msg.Data[6], msg.ErrorFlags)
                    )
                elif msg.Length == 8:
                    print(
                        "{} ({:>14}) : 0x{:02X} {} - {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} [{}]".format(
                            msg.TimeStamp, delta, msg.FrameId, msg.Length,
                            msg.Data[0],
                            msg.Data[1],
                            msg.Data[2],
                            msg.Data[3],
                            msg.Data[4],
                            msg.Data[5],
                            msg.Data[6],
                            msg.Data[7], msg.ErrorFlags)
                    )
                    '''
            else:
                self.linStatus = False

            time.sleep(0.00001)
        '''
        for msg in self.listMsg:
            print('\n - ' + msg)
        '''


    def displayMenuInput(self, text="Select an action: "):
        """
        Requests input from user

        Paramaters:
            text    custom text to display to the user

        Returns:
            User input as string (to upper)
        """
        choice = input(str.format("\n * {0}", text))
        # get user input
        # return the response as a upper string
        choice = str(choice).upper()
        print("\n")
        return choice

    def writeawakeupMessage(self, linmessage):
        # choice = "3C081B021060"
        # choice = "38"
        choice = linmessage
        print("choise")
        print(choice)
        try:
            # read frame ID
            if (choice == "38"):
                frameId = 56
            if (choice == "3C"):
                frameId = 60

            ##print("framme id")
            ##print(int(frameId))
            frameId = int(choice, 16)
            lFrameEntry = PLinApi.TLINFrameEntry()
            lFrameEntry.FrameId = c_ubyte(frameId)
            # print("debug tkd   " + str(lFrameEntry.FrameId))
            # get data length from frame
            linResult = self.m_objPLinApi.GetFrameEntry(
                self.m_hHw, lFrameEntry)
            # initialize LIN message to sent
            pMsg = PLinApi.TLINMsg()
            pMsg.Direction = PLinApi.TLINDirection(
                lFrameEntry.Direction)
            pMsg.ChecksumType = PLinApi.TLINChecksumType(
                lFrameEntry.ChecksumType)
            pMsg.Length = c_ubyte(lFrameEntry.Length)
            pMsg.Direction = PLinApi.TLIN_DIRECTION_PUBLISHER.value
            print("PLinApi.TLIN_DIRECTION_PUBLISHER.value  = ", PLinApi.TLIN_DIRECTION_PUBLISHER.value)
            # query and fill data, only if direction is publisher
            '''
            if (pMsg.Direction == PLinApi.TLIN_DIRECTION_PUBLISHER.value):
                for i in range(lFrameEntry.Length):
                    choice = self.displayMenuInput(
                        str.format('Data[{0}] (hex) : ', i + 1))
                    pMsg.Data[i] = c_ubyte(int(choice, 16))
            '''
            if (choice == "3C"):
                pMsg.Data[0] = c_ubyte(27)
                pMsg.Data[1] = c_ubyte(2)
                pMsg.Data[2] = c_ubyte(16)
                pMsg.Data[3] = c_ubyte(96)
                pMsg.Data[4] = c_ubyte(0)
                pMsg.Data[5] = c_ubyte(0)
                pMsg.Data[6] = c_ubyte(0)
                pMsg.Data[7] = c_ubyte(0)
            if (choice == "38"):
                pMsg.Data[0] = c_ubyte(0)

            # Check if the hardware is initialized as master
            if (self.m_HwMode.value == PLinApi.TLIN_HARDWAREMODE_MASTER.value):
                # set frame id to Protected ID
                nPID = c_ubyte(frameId)
                linResult = self.m_objPLinApi.GetPID(nPID)
                pMsg.FrameId = c_ubyte(nPID.value)
                # set checksum
                linResult = self.m_objPLinApi.CalculateChecksum(pMsg)
                # write LIN message
                linResult = self.m_objPLinApi.Write(
                    self.m_hClient, self.m_hHw, pMsg)
            else:
                # connected as slave : writing corresponds to updating
                # the data from LIN frame
                linResult = self.m_objPLinApi.UpdateByteArray(
                    self.m_hClient, self.m_hHw, c_ubyte(frameId), c_ubyte(0), c_ubyte(pMsg.Length), pMsg.Data)
            if (linResult == PLinApi.TLIN_ERROR_OK):
                print(pMsg.FrameId)
                print(pMsg.Length)
                print(pMsg.Direction)
                for i in data:
                    print(i)
                #self.displayNotification(
                #    "Message successfully written")
            else:
                print("eeror")
                #self.displayError(linResult)
                #self.displayNotification("Failed to write message")
        except:
            # catch all exception (LIN, bad input)
            print("eeror exception")
            #self.displayNotification()


if __name__ == '__main__':
    import threading

    appLin_Volvo = Lin_Peak_For_Volvo()
    appLin_Volvo.connect("appLin_Volvo", 1, 1)
    time.sleep(1)
    appLin_Volvo.disconnect()
    time.sleep(1)
    appLin_Volvo.connect("appLin_Volvo", 1, 1)
    appLin_Volvo.set_global_frame_table()
    time.sleep(1)
    #appLin_Volvo.get_global_frame_table()
    #appLin_Volvo.displayMenuInput("** Press <enter to stop schedule **")
    time.sleep(1)
    appLin_Volvo.delete_schedule_table(0)
    time.sleep(1)
    appLin_Volvo.set_schedule_table(0)
    #time.sleep(1)
    #appLin_Volvo.get_schedule_table(0)

    '''appLin_Volvo.update_schedule_data(0x38, [0x01, 0x01])
    appLin_Volvo.update_schedule_data(0x3C, [0x1B,0x02,0x10,0x60,0x00,0x00,0x00,0x00])
    appLin_Volvo.update_schedule_data(0x2B, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    appLin_Volvo.update_schedule_data(0x30, [0x00, 0x00, 0x00, 0x00])
    appLin_Volvo.update_schedule_data(0x31, [0x00, 0x00, 0x00, 0x00])
    appLin_Volvo.update_schedule_data(0x20, [0x00, 0x00])
    appLin_Volvo.update_schedule_data(0x37, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    '''

    
    appLin_Volvo.start_schedule_table(0)
    appLin_Volvo.read()
    '''
    appLin_Volvo.displayMenuInput("** Press <enter to stop schedule **")
    appLin_Volvo.update_schedule_data(0x3C, [0x1B, 0x02, 0x10, 0x60, 0x00, 0x00, 0x00, 0x00])
    appLin_Volvo.displayMenuInput("** Press <enter to stop schedule **")
    while(1):
        data = [0x1B,0x00,0x10,0x15,0x00,0x00,0x00,0x00]
        appLin_Volvo.write_frame(0x37, data)
        appLin_Volvo.update_schedule_data(0x3C, [0x1B, 0x02, 0x10, 0x60, 0x00, 0x00, 0x00, 0x00])
        time.sleep(0.1)
    appLin_Volvo.read()'''
    appLin_Volvo.suspend_schedule_table()
    appLin_Volvo.delete_schedule_table(0)
    appLin_Volvo.disconnect()
