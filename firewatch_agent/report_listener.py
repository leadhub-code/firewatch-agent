from collections import namedtuple
from datetime import datetime
import logging
import requests


logger = logging.getLogger(__name__)


Event = namedtuple('Event', 'log_path date chunk')


class ReportWarningListener:
    '''
    Listens for warning events and sends them via HTTP.
    '''

    max_count = 100

    def __init__(self, report_url, agent_id, system, rs=None):
        self.report_url = report_url
        self.agent_id = agent_id
        self.system = system
        self.rs = rs or requests.session()
        self.events_to_report = []
        self.skipped = 0

    def add_event(self, event):
        logger.debug('%s.add_event(%r)', self.__class__.__name__, event)
        assert isinstance(event.log_path, str)
        assert isinstance(event.date, datetime)
        assert isinstance(event.chunk, bytes)
        if len(self.events_to_report) < self.max_count:
            self.events_to_report.append(event)
        else:
            self.skipped += 1

    def flush(self):
        if self.skipped:
            logger.warning('Too many events - %d events were skipped', self.skipped)
            self.skipped = 0
        data = {
            'firewatch_report': {
                'agent_id': self.agent_id,
                'host': self.system.getfqdn(),
                'events': [{
                    'date': ev.date.isoformat(),
                    'log_path': ev.log_path,
                    'chunk': ev.chunk.decode(),
                } for ev in self.events_to_report],
            },
        }
        r = self.rs.post(self.report_url, json=data)
        r.raise_for_status()
        self.events_to_report = []
