from collections import deque
import logging
import os


logger = logging.getLogger(__name__)


class Reader:

    def __init__(self, log_path, log_conf, system):
        self.log_path = log_path
        self.log_conf = log_conf
        self.stream = log_path.open('rb')
        self.last_lines = deque(maxlen=100)
        self.interest_lines = None
        self.interest_deadline = None
        self.interest_context = 0

    def get_inode(self):
        return os.stat(self.stream.fileno()).st_ino

    def run(self):
        while True:
            line = self.stream.readline()
            if not line:
                break
            logger.debug('%s line: %r', self.log_path, line)
