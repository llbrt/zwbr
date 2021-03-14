import logging
import sys

class ProgressBar:
    """ Print or log progress."""

    def __init__(self, total, prefix = "", suffix = "", length = 50, fill = '█'):
        self._log = not sys.stdout.isatty()
        self._total = total
        if self._log:
            self._prefix = prefix
        else:
            self._prefix = "INFO: " + prefix
        self._suffix = suffix
        self._length = length
        self._fill = fill

    def print(self, iteration):
        """ Progressing. """
        if self._log:
            logging.info("%s %3d%% %s" % (self._prefix, 100 * iteration // self._total, self._suffix))
        else:
            percent = "{0:d}".format(int(100 * iteration // self._total))
            filledLength = int(self._length * iteration // self._total)
            bar = self._fill * filledLength + '-' * (self._length - filledLength)
            print(f'\r{self._prefix} |{bar}| {percent}% {self._suffix}', end = "\r")

        if iteration == self._total: 
            self.done()

    def done(self):
        """ New line to end progress. """
        if not self._log:
            print()
