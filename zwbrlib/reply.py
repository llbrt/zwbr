import logging
import csv

class NotAController(Exception):
    pass

class NodesNotFound(Exception):
    pass

class ReplySerialApiGetGetInitData:

    MAXIMUM_NODE_COUNT = 29

    CHIP_BY_TYPE_VERSION = {
        "0102": "ZW0102",
        "0201": "ZW0201",
        "0301": "ZW0301",
        "0401": "SD3402",
        "0500": "ZW050x",
        }

    def __init__(self, frame: bytes):
        init_capabilities = frame[5]
        if (init_capabilities & 0x1) != 0:
            raise NotAController
        if frame[6] != ReplySerialApiGetGetInitData.MAXIMUM_NODE_COUNT:
            raise NodesNotFound
        
        self.is_primary = (init_capabilities & 0x4) == 0
        self.is_SIS = (init_capabilities & 0x8) != 0
        self.nodes = frame[7:7 + ReplySerialApiGetGetInitData.MAXIMUM_NODE_COUNT]
        logging.debug("nodes=%s (len=%d)" % (self.nodes.hex(), len(self.nodes)))

        chip_offset = len(frame) - 3
        chip_id_version = "%02X%02X" % (frame[chip_offset], frame[chip_offset + 1])
        self.chip = ReplySerialApiGetGetInitData.CHIP_BY_TYPE_VERSION.get(chip_id_version, "unknown")

class ReplySerialApiGetCapabilities:

    def __init__(self, frame: bytes):
        self.serial_api_version = "%d.%d" % (frame[4], frame[5])
        self.manufacturer_id = "0x%02X%02X" % (frame[6], frame[7])
        self.product_type = "0x%02X%02X" % (frame[8], frame[9])
        self.product_id = "0x%02X%02X" % (frame[10], frame[11])
        self.funcid_supported = frame[12:len(frame)]
        logging.debug("func id=%s (len=%d)" % (self.funcid_supported.hex(), len(self.funcid_supported)))

        # Look for manufacturer name
        self.manufacturer = '?'
        with open('manufacturers-2020-07-01.csv', newline='') as manufacturers:
            reader = csv.DictReader(manufacturers)
            for row in reader:
                if row['ID'] == self.manufacturer_id:
                    self.manufacturer = row['Manufacturer']
                    break

class ReplyGetVersion:

    LIBRARY_BY_TYPE = {
        1: "static controller",
        2: "controller",
        3: "enhanced slave",
        4: "slave",
        5: "installer",
        6: "routing slave",
        7: "bridge controller",
        8: "device under test",
        }

    def __init__(self, frame: bytes):
        len = frame[1]
        self.library_type = ReplyGetVersion.LIBRARY_BY_TYPE.get(frame[len], "unknown")
        self.version = str(frame[4:len - 1], 'utf-8')

class ReplyMemoryGetId:

    def __init__(self, frame: bytes):
        self.home_id = "%02X%02X%02X%02X" % (frame[4], frame[5], frame[6], frame[7])
        self.node_id = frame[8]

class ReplySetDefault:

    def __init__(self, frame: bytes):
        pass

class ReplyReadNVM:

    def __init__(self, frame: bytes):
        len = frame[1]
        self.data = frame[4:len + 1]

class ReplyWriteNVM:

    def __init__(self, frame: bytes):
        pass
