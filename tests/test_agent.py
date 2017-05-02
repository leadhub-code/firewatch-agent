import logging
from pathlib import Path
from textwrap import dedent
import yaml

from firewatch_agent.agent import Agent
from firewatch_agent.util import unique
from firewatch_agent.state_store import MemStateStore


logger = logging.getLogger(__name__)


class _Listener:

    def __init__(self, events):
        '''
        Created via get_test_listener().
        '''
        self._events = events

    def log_line(self, log_path, line):
        self._events.append(('log_line', log_path, line))

    def flush(self):
        self._events.append('flush')


class _CustomList (list):

    def pop_all(self):
        items = list(self)
        self.clear()
        return items


def get_test_listener():
    events = _CustomList()
    return (_Listener(events), events)


def test_one(tmp_dir):
    conf_file = tmp_dir / 'firewatch-logs.yaml'
    with conf_file.open('w') as f:
        f.write(dedent('''
            firewatch_logs:
                log_files:
                    - '*.log'
        '''))
    log_file = tmp_dir / 'some.log'
    with log_file.open('w') as f:
        f.write('cheese\n')
        f.write('tomato\n')
    state_store = MemStateStore()
    listener, events = get_test_listener()
    agent = Agent([tmp_dir], state_store, listener)
    agent.run_iteration()
    assert events.pop_all() == [
        ('log_line', str(log_file), b'cheese\n'),
        ('log_line', str(log_file), b'tomato\n'),
        'flush',
    ]
    with log_file.open('a') as f:
        f.write('bacon\n')
    agent.run_iteration()
    assert events.pop_all() == [
        ('log_line', str(log_file), b'bacon\n'),
        'flush',
    ]
