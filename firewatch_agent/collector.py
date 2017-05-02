from datetime import datetime
import logging

from .report_listener import Event


logger = logging.getLogger(__name__)


class Collector:

    def __init__(self, report_listener, system):
        self.report_listener = report_listener
        self._utcnow = system.utcnow

    def log_line(self, log_path, line):
        assert isinstance(log_path, str)
        assert isinstance(line, bytes)
        report = b'WARN' in line or b'ERR' in line
        if report:
            now = self._utcnow()
            self.report_listener.add_event(Event(
                log_path=log_path,
                date=now,
                chunk=line,
            ))

    def flush(self):
        self.report_listener.flush()
