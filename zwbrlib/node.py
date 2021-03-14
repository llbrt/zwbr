import xml.etree.ElementTree as ET
import logging

tree = ET.parse('open-zwave-device_classes.xml')
device_classes = tree.getroot()

DEVICE_CLASS_NAME_BASIC = '{https://github.com/OpenZWave/open-zwave}Basic'
DEVICE_CLASS_NAME_GENERIC = '{https://github.com/OpenZWave/open-zwave}Generic'
DEVICE_CLASS_NAME_SPECIFIC = '{https://github.com/OpenZWave/open-zwave}Specific'

def _find_class_basic(basic_id):
    class_ = _find_class(DEVICE_CLASS_NAME_BASIC, basic_id)
    if class_ != None:
        return class_.get('label')
    return "Unknown"

def _find_class_generic(generic_id):
    class_ = _find_class(DEVICE_CLASS_NAME_GENERIC, generic_id)
    if class_ != None:
        return class_.get('label')
    return "Unknown"

def _find_class_specific(generic_id, specific_id):
    class_ = _find_class(DEVICE_CLASS_NAME_GENERIC, generic_id)
    if class_ != None:
        subclass_ = _find_class_in_subtree(class_, DEVICE_CLASS_NAME_SPECIFIC, specific_id)
        if subclass_ != None:
            return subclass_.get('label')
    return "Unknown"

def _find_class(name, id):
    return _find_class_in_subtree(device_classes, name, id)

def _find_class_in_subtree(start, name, id):
    for class_ in start.findall(name):
        if int(class_.get('key'), 16) == id:
            return class_

class Node:

    def __init__(self, frame: bytes, node_id):
        self.node_id = node_id

        capabilities = frame[4]
        security = frame[5]
        class_basic = frame[7]
        class_generic = frame[8]
        class_specific = frame[9]

        self.version = (capabilities & 0x07) + 1
        self.routing = (capabilities & 0x40) != 0
        self.listening = (capabilities & 0x80) != 0
        if (capabilities & 0x38) == 0x10:
            self.max_baud_rate = 40000
        else:
            self.max_baud_rate = 9600

        self.security = (security & 0x01) != 0
        self.controller = (security & 0x02) != 0
        self.routing_slave = (security & 0x08) != 0
        self.beaming = (security & 0x10) != 0
        self.sensor_250ms = (security & 0x20) != 0
        self.sensor_1000ms = (security & 0x40) != 0

        self.class_basic = _find_class_basic(class_basic)
        self.class_generic = _find_class_generic(class_generic)
        self.class_specific = _find_class_specific(class_generic, class_specific)

    def log(self):
        logging.info("%03d basic class    %s" % (self.node_id, self.class_basic))
        logging.info("%03d generic class  %s" % (self.node_id, self.class_generic))
        logging.info("%03d specific class %s" % (self.node_id, self.class_specific))
        logging.info("%03d version        %s" % (self.node_id, self.version))
        logging.info("%03d routing        %s" % (self.node_id, self.routing))
        logging.info("%03d listening      %s" % (self.node_id, self.listening))
        logging.info("%03d max baud       %s" % (self.node_id, self.max_baud_rate))
        logging.info("%03d security       %s" % (self.node_id, self.security))
        logging.info("%03d controller     %s" % (self.node_id, self.controller))
        logging.info("%03d routing slave  %s" % (self.node_id, self.routing_slave))
        logging.info("%03d beaming        %s" % (self.node_id, self.beaming))
        logging.info("%03d sensor 250ms   %s" % (self.node_id, self.sensor_250ms))
        logging.info("%03d sensor 1000ms  %s" % (self.node_id, self.sensor_1000ms))
