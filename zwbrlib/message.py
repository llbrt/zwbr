import logging
import struct

import zwbrlib.reply as reply
from zwbrlib.node import Node as Node

# Type of frame
# indicates that the receiving end received a valid Data frame
FRAME_ACK = bytes([0x06])
# indicates that the receiving end received a Data frame with errors
FRAME_NAK = bytes([0x15])
# indicates that the receiving end discarded an otherwise valid Data frame
FRAME_CAN = bytes([0x18])
# Start Of Frame (data frame)
FRAME_SOF = bytes([0x01])

FRAME_DISCARDED = bytes([0xae])  # Received data discarded
FRAME_NONE      = bytes([0xaf])  # No frame received

TYPE_REQ = bytes([0x00])  # Request
TYPE_RES = bytes([0x01])  # Response

FUNC_ID_SERIAL_API_GET_INIT_DATA    = bytes([0x02]) # node list
FUNC_ID_SERIAL_API_GET_CAPABILITIES = bytes([0x07]) # version, details, list functions
FUNC_ID_SERIAL_API_SOFT_RESET       = bytes([0x08]) # soft reset the controller; no reply expected
FUNC_ID_ZW_GET_VERSION              = bytes([0x15])
FUNC_ID_ZW_MEMORY_GET_ID            = bytes([0x20]) # get homeid, nodeid
FUNC_ID_NVM_EXT_READ_LONG_BUFFER    = bytes([0x2A]) # read NVM offset (3? bytes) - len (2? byte)
FUNC_ID_NVM_EXT_WRITE_LONG_BUFFER   = bytes([0x2B]) # write NVM offset (3? bytes) - len (2? byte) - data (len bytes)
FUNC_ID_ZW_GET_NODE_PROTOCOL_INFO   = bytes([0x41]) # get node type

# <dangerous> Reset controller and node info to default (original) values
# Function with a callback
FUNC_ID_ZW_SET_DEFAULT              = bytes([0x42])
FUNC_ID_ZW_SET_DEFAULT_CB_ID        = bytes([0x12])

class Frame:

    def __init__(self, frame: bytes):
        # bytes of the frame
        self.frame = frame

    def is_ack(self):
        return self.frame[0] == FRAME_ACK[0]

    def is_nak(self):
        return self.frame[0] == FRAME_NAK[0]

    def is_can(self):
        return self.frame[0] == FRAME_CAN[0]

    def is_data(self):
        return self.frame[0] == FRAME_SOF[0]

    def is_request(self):
        return self.frame[2] == TYPE_REQ[0]

    def is_response(self):
        return self.frame[2] == TYPE_RES[0]

    def get_func_id(self):
        """ Function id of a data frame """
        return self.frame[3]

    def reply_SerialApiGetInitData(self):
        return self._response(FUNC_ID_SERIAL_API_GET_INIT_DATA[0], "SERIAL_API_GET_INIT_DATA", 'ReplySerialApiGetGetInitData')

    def reply_SerialApiGetCapabilities(self):
        return self._response(FUNC_ID_SERIAL_API_GET_CAPABILITIES[0], "SERIAL_API_GET_CAPABILITIES", 'ReplySerialApiGetCapabilities')

    def reply_GetVersion(self):
        return self._response(FUNC_ID_ZW_GET_VERSION[0], "GET_VERSION", 'ReplyGetVersion')

    def reply_MemoryGetId(self):
        return self._response(FUNC_ID_ZW_MEMORY_GET_ID[0], "MEMORY_GET_ID", 'ReplyMemoryGetId')

    def reply_SetDefault(self):
        if not self.is_data() or not self.is_request() or self.get_func_id() != FUNC_ID_ZW_SET_DEFAULT[0] or self.frame[4] != FUNC_ID_ZW_SET_DEFAULT_CB_ID[0]:
            logging.warn("Not the expected SET_DEFAULT request callback")
            return
        return reply.ReplySetDefault(self.frame)

    def reply_GetNodeProtocolInfo(self, node_id):
        """ returns a node or None """
        if not self.is_data() or not self.is_response() or self.get_func_id() != FUNC_ID_ZW_GET_NODE_PROTOCOL_INFO[0]:
            logging.warn("Not a GET_NODE_PROTOCOL_INFO response")
            return
        if self.frame[4] != 0:
            # existing node
            return Node(self.frame, node_id)

    def reply_ReadNVM(self):
        return self._response(FUNC_ID_NVM_EXT_READ_LONG_BUFFER[0], "NVM_READ", 'ReplyReadNVM')

    def reply_WriteNVM(self):
        return self._response(FUNC_ID_NVM_EXT_WRITE_LONG_BUFFER[0], "NVM_WRITE", 'ReplyWriteNVM')

    def _response(self, expected_func_id, func_name, reply_name):
        if not self.is_data() or not self.is_response() or self.get_func_id() != expected_func_id:
            logging.warn("Not a %s response" % func_name)
            return
        reply_builder = getattr(reply, reply_name)
        return reply_builder(self.frame)

class PayloadTooLargeError(Exception):
    pass

# Immutable utility frames
ack = Frame(FRAME_ACK)
nak = Frame(FRAME_NAK)
can = Frame(FRAME_CAN)
discarded = Frame(FRAME_DISCARDED)
none = Frame(FRAME_NONE)

def compute_checksum(length, payload: bytes):
    checksum = 0xFF ^ length
    for i in range(0, length - 1):
        checksum ^= payload[i]
    return checksum

def request_SerialApiGetInitData():
    return _request_void(FUNC_ID_SERIAL_API_GET_INIT_DATA)

def request_SerialApiGetCapabilities():
    return _request_void(FUNC_ID_SERIAL_API_GET_CAPABILITIES)

def request_SoftReset():
    return _request_void(FUNC_ID_SERIAL_API_SOFT_RESET)

def request_GetVersion():
    return _request_void(FUNC_ID_ZW_GET_VERSION)

def request_MemoryGetId():
    return _request_void(FUNC_ID_ZW_MEMORY_GET_ID)

def _request_void(funcid):
    return Frame(_data(TYPE_REQ + funcid))

def request_SetDefault():
    return Frame(_data(TYPE_REQ + FUNC_ID_ZW_SET_DEFAULT + FUNC_ID_ZW_SET_DEFAULT_CB_ID))

def request_GetNodeProtocolInfo(node_id):
    return Frame(_data(TYPE_REQ + FUNC_ID_ZW_GET_NODE_PROTOCOL_INFO + bytes([node_id])))

def request_ReadNVM(offset, len):
    return Frame(_data(TYPE_REQ + FUNC_ID_NVM_EXT_READ_LONG_BUFFER + _encode_NVM_op_args(offset, len)))

def request_WriteNVM(offset, data_to_write: bytes):
    return Frame(_data(TYPE_REQ + FUNC_ID_NVM_EXT_WRITE_LONG_BUFFER + _encode_NVM_op_args(offset, len(data_to_write)) + data_to_write))

def _encode_NVM_op_args(offset, len):
    return struct.pack(">I", offset)[1:5] + bytes([0, len])

def _data(payload: bytes):
    length = len(payload) + 1
    if length > 252:
        raise PayloadTooLargeError
    checksum = compute_checksum(length, payload)
    return FRAME_SOF + bytes([length]) + payload + bytes([checksum])
