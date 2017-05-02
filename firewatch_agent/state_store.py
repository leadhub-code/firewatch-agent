'''
State store is used for keeping track what parts of which log files are
already processed so we don't process them again when the program is restarted.
'''

import logging
import os
import yaml


logger = logging.getLogger(__name__)


class MemStateStore:
    '''
    Memory-only store used in tests
    '''

    def __init__(self):
        self.state = {}
        self.committed = False

    def update(self, path, path_state):
        logger.debug('State update: %s %r', path, path_state)
        self.state[path] = path_state
        self.committed = False

    def get(self, path):
        return self.state.get(path)

    def commit(self):
        self.committed = True


class YAMLStateStore:
    '''
    Based on YAML files
    '''

    def __init__(self, path):
        self.path = path
        self.last_stat = None
        self.data = None
        self.updates = {}

    def _last_stat_value(self, st):
        return (st.st_size, st.st_mtime, st.st_ino)

    def _load(self):
        logger.debug('Loading state from %s', self.path)
        try:
            with self.path.open() as f:
                st = os.stat(f.fileno())
                self.data = yaml.safe_load(f)
                self.last_stat = self._last_stat_value(st)
        except FileNotFoundError as e:
            self.data = {}
            self.last_stat = None
        if 'firewatch_agent_states' not in self.data:
            self.data['firewatch_agent_states'] = {}

    def get(self, key):
        if key in self.updates:
            return self.updates[key]
        if self.data is None:
            self._load()
        return self.data['firewatch_agent_states'].get(key)

    def update(self, key, value):
        self.updates[key] = value

    def commit(self):
        try:
            current_stat = self._last_stat_value(os.stat(str(self.path)))
        except FileNotFoundError as e:
            current_stat = None
        if current_stat != self._last_stat_value:
            self._load()
        for k, v in self.updates.items():
            self.data['firewatch_agent_states'][k] = v
        temp_file = self.path.with_name('.{}.temp'.format(self.path.name))
        with temp_file.open('w') as f:
            yaml.safe_dump(self.data, f)
        temp_file.rename(self.path)
        self.last_stat = self._last_stat_value(os.stat(str(self.path)))
        self.updates = {}
        logger.info('State saved to %s', self.path)
