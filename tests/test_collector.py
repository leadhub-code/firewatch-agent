from datetime import datetime
import logging

from firewatch_agent.report_listener import Event
from firewatch_agent.collector import Collector


logger = logging.getLogger(__name__)


class _ReportListener:

    def __init__(self, calls):
        self._calls = calls

    def add_event(self, event):
        self._calls.append(('add_event', event))

    def flush(self):
        self._calls.append('flush')


class _CustomList (list):

    def pop_all(self):
        items = list(self)
        self.clear()
        return items


def get_test_report_listener():
    calls = _CustomList()
    return (_ReportListener(calls), calls)


def test_collector(system):
    report_listener, rl_calls = get_test_report_listener()
    collector = Collector(report_listener, system=system)
    collector.log_line('/some.log', b'2016-04-27 12:00:01 [p1] INFO: cheese\n')
    collector.log_line('/some.log', b'2016-04-27 12:00:02 [p2] INFO: onion\n')
    collector.log_line('/some.log', b'2016-04-27 12:00:03 [p1] WARNING: bacon\n')
    collector.flush()
    assert rl_calls.pop_all() == [
        ('add_event', Event(
            log_path='/some.log',
            date=datetime(2017, 4, 27, 12, 0),
            chunk=b'2016-04-27 12:00:03 [p1] WARNING: bacon\n')),
        'flush',
    ]
