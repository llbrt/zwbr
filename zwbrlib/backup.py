import logging
import os

from zwbrlib.controller import Controller as Controller
from zwbrlib.dataoperation import DataOperation as DtOp
import zwbrlib.message as message

class BackupFailed(Exception):
    pass

class ZwBackup(DtOp):
    """ Backup operation"""

    def __init__(self, controller: Controller, file):
        super().__init__("Backup ")
        self._controller = controller
        self._file = file
        self._started = False
        self._success = False

    def __del__(self):
        if self._started and not self._success:
            os.remove(self._file)
            logging.info("File '%s' removed" % self._file)

    def exec(self):
        logging.info("--- backup ------")
        with open(self._file, "xb") as f:
            self._started = True
            for count in range(0, DtOp.block_count):
                reply_read = self._controller.request(message.request_ReadNVM(count * DtOp.block_size, DtOp.block_size), 'reply_ReadNVM')
                if reply_read == None:
                    self.progressDone()
                    raise BackupFailed("Read NVM failed")
                f.write(reply_read.data)
                self.progress(count + 1)

        # Check the size of the file
        file_size = os.stat(self._file).st_size
        if file_size != self.getExpectedSize():
            raise BackupFailed("Wrong file size %d <> %d" % (file_size, self.getExpectedSize()))

        self._success = True
        logging.info("--- done --------")
