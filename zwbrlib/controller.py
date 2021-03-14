import serial
import time
import logging

import zwbrlib.message as message
from zwbrlib.message import Frame as Frame

class ProtocolError(Exception):
    pass

class Controller:
    """Z-Wave controller accessible through a serial port"""

    def __init__(self, device):
        self.__device = serial.Serial(port=device,  baudrate=115200)
        self.__device.timeout = 5
        logging.debug(self.__device)
        self._write_frame(message.nak)
        time.sleep(1)

    def __del__(self):
        try:
            if self.__device.isOpen():
                self.close()
            logging.debug(self.__device)
        except:
            pass

    def close(self):
        self.__device.close()

    def soft_reset(self):
        """ Performs a soft reset of the controller.
        The opened handler may not be valid after this call"""
        logging.debug("Soft reset requested")
        request_frame = message.request_SoftReset()
        self._write_frame(request_frame)
        time.sleep(2)
        logging.debug("Soft reset done")

    def request(self, request_frame: Frame, reply_name, reply_arg1 = None):
        reply_frame = self._get_reply_frame(request_frame)
        if reply_frame != None:
            reply_builder = getattr(reply_frame, reply_name)
            if reply_arg1 == None:
                return reply_builder()
            else:
                return reply_builder(reply_arg1)

    def _get_reply_frame(self, request_frame: Frame) -> Frame:
        """ Returns the reply frame of the given request or None on failure """
        expected_func_id = request_frame.get_func_id()
        for i in range(20):
            self._write_frame(request_frame)
            if not self._ack_received():
                # Retry
                continue

            frame = self._read_frame()
            if frame.is_data() and expected_func_id == frame.get_func_id():
                self._write_frame(message.ack)
                return frame
            self._accept_ignorable_frame(frame)

    def _ack_received(self):
        frame = self._read_frame()
        if frame.is_ack():
            return True
        self._accept_ignorable_frame(frame)
        return False

    def _accept_ignorable_frame(self, frame: Frame):
        if frame.is_data():
            # ACK data (especially request command handler, func_id=0x04)
            self._write_frame(message.ack)
            logging.debug("Ignoring frame function %d" % frame.get_func_id())
        elif frame.is_can():
            # Ignore CAN
            logging.debug("CAN received")
        else:
            logging.error("Unexpected frame %s" % frame.frame.hex())
            raise ProtocolError("Unexpected frame received")

    def _write_frame(self, frame: Frame):
        logging.debug("To write %s/%d" % (frame.frame.hex(), len(frame.frame)))
        n = self.__device.write(frame.frame)
        self.__device.flush()
        logging.debug("wrote %d" % (n))

    def _read_frame(self) -> Frame:
        """ Returns a frame read or a dummy frame when data have been discarded """
        type = self.__device.read()
        if len(type) < 1:
            logging.debug("No frame read")
            return message.none

        frame = Frame(type)
        if not frame.is_data():
            logging.debug("Read %s/%d" % (frame.frame.hex(), len(frame.frame)))
            return frame

        # Read data frame
        length = self.__device.read()[0]
        payload = self.__device.read(length)
        expected_checksum = payload[length-1]
        # Verify checksum
        checksum = message.compute_checksum(length, payload)
        if expected_checksum != checksum:
            # Discard data, including pending data
            logging.debug("Discard invalid frame (checksum); consume pending data")
            waiting = self.__device.in_waiting()
            if waiting > 0:
                self.__device.read(waiting)

            return message.discarded

        # Return frame (without checksum)
        frame = Frame(type + bytes([length]) + payload)
        logging.debug("Read %s/%d" % (frame.frame.hex(), len(frame.frame)))
        return frame
