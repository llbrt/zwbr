from zwbrlib.progress import ProgressBar

class DataOperation:

    # Part of the NVM to read/write
    block_size = 128
    block_count = 48

    def __init__(self, operation_name):
        self._progress = ProgressBar(DataOperation.block_count, prefix = operation_name, suffix = "complete")

    def progress(self, iteration):
        self._progress.print(iteration)

    def progressDone(self):
        self._progress.done()

    def getExpectedSize(self):
        return DataOperation.block_size * DataOperation.block_count
