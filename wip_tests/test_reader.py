import logging
import os

from firewatch_agent.reader import Reader


logger = logging.getLogger(__name__)


class StateStore:

    def __init__(self):
        self.state = {}

    def update(self, path, path_state):
        logger.debug('State update: %s %r', path, path_state)
        self.state[path] = path_state

    def get(self, path):
        return self.state.get(path)


def test_reader_follows_file(tmp_dir):
    log_file = tmp_dir / 'some.log'
    with log_file.open('w') as f:
        f.write('cheese\n')
        f.write('tomato\n')
    reader = Reader(log_file)
    assert list(reader.read()) == [b'cheese\n', b'tomato\n']
    assert list(reader.read()) == []
    with log_file.open('a') as f:
        f.write('bacon\n')
    assert list(reader.read()) == [b'bacon\n']


def test_reader_doesnt_return_unfinished_lines(tmp_dir):
    log_file = tmp_dir / 'some.log'
    with log_file.open('w') as f:
        f.write('chee')
    reader = Reader(log_file)
    assert list(reader.read()) == []
    with log_file.open('a') as f:
        f.write('se\nbac')
    assert list(reader.read()) == [b'cheese\n']
    with log_file.open('a') as f:
        f.write('on\n')
    assert list(reader.read()) == [b'bacon\n']


def test_reader_handles_file_inode_change(tmp_dir):
    log_file = tmp_dir / 'some.log'
    with log_file.open('w') as f:
        f.write('cheese\n')
        f.write('tomato\n')
    reader = Reader(log_file)
    assert list(reader.read()) == [b'cheese\n', b'tomato\n']
    # the inode could be reused if we just unlinked log_file
    log_file.rename(log_file.with_name('some.log.rotated'))
    with log_file.open('w') as f:
        f.write('bacon\n')
        f.write('eggs\n')
        f.write('onion\n')
    assert list(reader.read()) == [b'bacon\n', b'eggs\n', b'onion\n']


def test_reader_handles_shrinked_file(tmp_dir):
    # rotated logs could have reused inode, but they should have smaller size
    log_file = tmp_dir / 'some.log'
    with log_file.open('w') as f:
        f.write('cheese\n')
        f.write('tomato\n')
    reader = Reader(log_file)
    assert list(reader.read()) == [b'cheese\n', b'tomato\n']
    with log_file.open('w') as f:
        f.write('bacon\n')
    assert list(reader.read()) == [b'bacon\n']


def test_reader_remembers_position(tmp_dir):
    log_file = tmp_dir / 'some.log'
    with log_file.open('w') as f:
        f.write('cheese\n')
        f.write('tomato\n')
    state_store = StateStore()
    reader = Reader(log_file, state_store)
    assert list(reader.read()) == [b'cheese\n', b'tomato\n']
    with log_file.open('a') as f:
        f.write('bacon\n')
    reader = Reader(log_file, state_store)
    assert list(reader.read()) == [b'bacon\n']
