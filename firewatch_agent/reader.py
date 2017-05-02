import logging
import os


logger = logging.getLogger(__name__)


class Reader:
    '''
    Reads a log file.

    Can handle log rotation.
    Works with State store, so when started again on a file that was previously
    processed it continues from the last position.
    '''

    def __init__(self, path, state_store=None):
        self.path = path
        self.state_store = state_store
        self.f = None
        self.f_inode = None
        self.f_size = 0
        self.f_pos = 0
        self.carry = None

    def read(self):
        while True:
            if self.f is None:
                self.f = self.path.open('rb')
                self.f_pos = 0
                st = os.stat(self.f.fileno())
                self.f_inode = {'ino': st.st_ino, 'dev': st.st_dev}
                self.f_size = st.st_size
                if self.state_store:
                    saved_state = self.state_store.get(str(self.path))
                    use_state = (
                        saved_state
                        and saved_state['inode'] == self.f_inode
                        and saved_state['position'] <= self.f_size)
                    if use_state:
                        self.f.seek(saved_state['position'])
                        self.f_pos = self.f.tell()
            # read file lines
            while True:
                line = self.f.readline()
                if not line:
                    break
                if line.endswith(b'\n'):
                    if self.carry is not None:
                        line = self.carry + line
                        self.carry = None
                    self.f_pos = self.f.tell()
                    yield line
                else:
                    self.carry = (self.carry or b'') + line
            # check that our opened file was not rotated
            st = os.stat(str(self.path))
            current_inode = {'ino': st.st_ino, 'dev': st.st_dev}
            if current_inode == self.f_inode and st.st_size >= self.f_size:
                self.f_size = st.st_size
                break
            else:
                logger.debug('Reopening file %s (inode has changed)', self.path)
                if self.carry is not None:
                    yield self.carry
                    self.carry = None
                self.f = None
                self.f_inode = None
                self.f_size = 0
                self.f_pos = 0
                continue
        if self.state_store is not None:
            if self.f is None:
                self.state_store.update(str(self.path), None)
            else:
                self.state_store.update(str(self.path), {
                    'inode': self.f_inode,
                    'position': self.f_pos,
                })

    def _stat_inode(self, f):
        # f is path or fileno
        st = os.stat(f)
        return (st.st_ino, st.st_dev)
