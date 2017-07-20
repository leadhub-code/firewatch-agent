import logging
import os

try:
    import simplejson as json
except ImportError:
    import json


logger = logging.getLogger(__name__)


class StateFile:

    def __init__(self, path):
        self.path = path
        self.data = None
        self.stat = None
        self._load()

    def __repr__(self):
        return '<{cls} {s.path}>'.format(cls=self.__class__.__name__, s=self)

    def _load(self):
        if not self.path.exists():
            logger.debug('State file does not exist: %s', self.path)
            self.data = {}
        else:
            with self.path.open() as f:
                self.data = json.load(f)['firewatch_agent_state']
                st = os.stat(f.fileno())
                self.stat = self._get_stat_key(st)
            logger.debug('State file loaded: %s', self.path)

    def save(self):
        tmp_path = self.path.with_name(self.path.name + '.tmp')
        with tmp_path.open('w') as f:
            json.dump({'firewatch_agent_state': self.data}, f, indent=2)
            f.write('\n')
            f.flush()
            st = os.stat(f.fileno())
        tmp_path.rename(self.path)
        self.stat = self._get_stat_key(st)

    def _get_stat_key(self, st):
        return (st.st_size, st.st_mtime)
