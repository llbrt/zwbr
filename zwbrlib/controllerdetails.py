import logging

import zwbrlib.bits as bits
from zwbrlib.controller import Controller as Controller
import zwbrlib.message as message

class DeviceNotAvailable(Exception):
    pass

class ControllerDetails:

    def __init__(self, controller: Controller):

        # Get serial api init data, get node list
        reply_api_init_data = controller.request(message.request_SerialApiGetInitData(), 'reply_SerialApiGetInitData')
        if reply_api_init_data == None:
            logging.error("The device is busy or is not a Z-Wave controller")
            raise DeviceNotAvailable

        self.is_primary = reply_api_init_data.is_primary
        self.is_SIS = reply_api_init_data.is_SIS
        self.chip = reply_api_init_data.chip
        self.nodes = reply_api_init_data.nodes

        # Get type and version
        reply_version = controller.request(message.request_GetVersion(), 'reply_GetVersion')
        self.type = reply_version.library_type
        self.version = reply_version.version

        # Get home id and node id
        reply_ids = controller.request(message.request_MemoryGetId(), 'reply_MemoryGetId')
        self.home_id = reply_ids.home_id
        self.node_id = reply_ids.node_id

        # Get serial api version and ids; supported functions
        reply_api_capabilities = controller.request(message.request_SerialApiGetCapabilities(), 'reply_SerialApiGetCapabilities')
        self.serial_api_version = reply_api_capabilities.serial_api_version
        self.manufacturer = reply_api_capabilities.manufacturer
        self.manufacturer_id = reply_api_capabilities.manufacturer_id
        self.product_type = reply_api_capabilities.product_type
        self.product_id = reply_api_capabilities.product_id
        self.funcid_supported = reply_api_capabilities.funcid_supported

    def log(self):
        logging.info("--- controller --")
        logging.info("type                %s" % self.type)
        logging.info("version             %s" % self.version)
        logging.info("serial API version  %s" % self.serial_api_version)
        logging.info("home id             %s" % self.home_id)
        logging.info("node id             %d" % self.node_id)
        logging.info("primary             %s" % self.is_primary)
        logging.info("SIS                 %s" % self.is_SIS)
        logging.info("chip                %s" % self.chip)
        logging.info("manufacturer        %s" % self.manufacturer)
        logging.info("manufacturer id     %s" % self.manufacturer_id)
        logging.info("product type        %s" % self.product_type)
        logging.info("product id          %s" % self.product_id)
        logging.info("read NVM supported  %s" % bits.is_id_set(self.funcid_supported, message.FUNC_ID_NVM_EXT_READ_LONG_BUFFER[0]))
        logging.info("write NVM supported %s" % bits.is_id_set(self.funcid_supported, message.FUNC_ID_NVM_EXT_WRITE_LONG_BUFFER[0]))
