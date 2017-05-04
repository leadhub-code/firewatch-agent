from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
from pytest import fixture


logging.basicConfig(
    format='~ %(name)-20s %(levelname)5s: %(message)s',
    level=logging.DEBUG)


if os.environ.get('DEBUG_HTTP_CLIENT'):
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = 1


@fixture
def tmp_dir(tmpdir):
    '''
    Return standard Path object instead of py.LocalPath from tmpdir fixture
    '''
    return Path(str(tmpdir))


@fixture
def system():
    return _System()


@fixture
def add_time(system):
    def f(**kwargs):
        system._now += timedelta(**kwargs)
    return f


class _System:

    def __init__(self):
        self._now = datetime.strptime('2017-04-27 12:00:00', '%Y-%m-%d %H:%M:%S')

    def utcnow(self):
        return self._now
