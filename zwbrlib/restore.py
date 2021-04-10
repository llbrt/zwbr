import logging
import os
from random import SystemRandom as SystemRandom

from zwbrlib.controller import Controller as Controller
from zwbrlib.controllerdetails import ControllerDetails as ControllerDetails
from zwbrlib.dataoperation import DataOperation as DtOp
import zwbrlib.message as message

class RestorationFailed(Exception):
    pass

class RestorationCancelled(Exception):
    pass

class ZwRestoration(DtOp):

    def __init__(self, controller: Controller, controller_details: ControllerDetails, file):
        super().__init__("Restore")

        # Verify file size
        if os.fstat(file.fileno()).st_size != self.getExpectedSize():
            raise RestorationFailed("Invalid source file (wrong size)")

        self._controller = controller
        self._controller_details = controller_details
        self._file = file
        self._success = False

    def exec(self):
        logging.info("--- restore -----")
        self._confirm_restore()
        logging.info("--- restoring ---")

        # Hard reset of the controller
        reply_set_default = self._controller.request(message.request_SetDefault(), 'reply_SetDefault')
        if reply_set_default == None:
            raise RestorationFailed("Failed to reset controller")

        for count in range(0, DtOp.block_count):
            to_write = self._file.read(DtOp.block_size)
            reply_write = self._controller.request(message.request_WriteNVM(count * DtOp.block_size, to_write), 'reply_WriteNVM')
            if reply_write == None:
                self.progressDone()
                raise RestorationFailed("Write NVM failed")
            
            self.progress(count + 1)

        self._success = True

        # Soft reset the controller to take the new NVM into account
        self._controller.soft_reset()

    def _confirm_restore(self):
        logging.info("")
        logging.info("+++++++++++++++++")
        logging.info("+  DISCLAIMER   +")
        logging.info("+++++++++++++++++")
        logging.info("This operation may damage your device.")
        logging.info("This software does NOT provide any guarantee of any kind.")
        logging.info("Continue at your own risks.")
        logging.info("+++++++++++++++++")
        self._expected_input("Enter \"I won't blame anyone but me\": ", "I won't blame anyone but me")
        self._enter_controller_info()

    def _enter_controller_info(self):
        random = SystemRandom()
        info = random.randint(1, 5)
        if info == 1:
            self._expected_input("Enter home id: ", self._controller_details.home_id)
        elif  info == 2:
            self._expected_input("Enter chip: ", self._controller_details.chip)
        elif  info == 3:
            self._expected_input("Enter manufacturer: ", self._controller_details.manufacturer)
        elif  info == 4:
            self._expected_input("Enter manufacturer id: ", self._controller_details.manufacturer_id)
        else:
            self._expected_input("Enter product id: ", self._controller_details.product_id)

    def _expected_input(self, prompt, expected):
        for i in range(5):
            text = input(prompt)
            if expected == text:
                return
        raise RestorationCancelled
