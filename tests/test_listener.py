from datetime import datetime
import flask
import logging
import multiprocessing
from pprint import pprint
import requests
from time import sleep
import yaml

from firewatch_agent.report_listener import ReportWarningListener, Event

from helpers import get_free_tcp_port


logger = logging.getLogger(__name__)


def server(port, started, received):
    app = flask.Flask(__name__)

    @app.route('/ping')
    def ping():
        return 'pong'

    @app.route('/report', methods=['POST'])
    def report():
        received.append(('report', flask.request.get_json()))
        return flask.jsonify({'ok': True})

    started.set()
    app.run(port=port, debug=False)


def test_listener(system):
    port = get_free_tcp_port()
    base_url = 'http://127.0.0.1:{}'.format(port)
    with multiprocessing.Manager() as manager:
        received = manager.list()
        started = manager.Event()
        p = multiprocessing.Process(target=server, args=(port, started, received))
        try:
            p.start()
            started.wait(3)
            assert started.is_set()
            sleep(.05)
            assert requests.get(base_url + '/ping').text == 'pong'
            # test server is now ready...
            listener = ReportWarningListener(base_url + '/report', agent_id='A1', system=system)
            dt = lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
            listener.add_event(Event('/some/service.log', dt('2016-04-27 12:00:01'), b'cheese\n'))
            listener.add_event(Event('/some/service.log', dt('2016-04-27 12:00:05'), b'tomato\n'))
            listener.flush()
            pprint(list(received))
            assert list(received) == [
                ('report', {
                    'firewatch_report': {
                        'agent_id': 'A1',
                        'host': 'server.example.com',
                        'events': [
                            {
                                'chunk': 'cheese\n',
                                'date': '2016-04-27T12:00:01',
                                'log_path': '/some/service.log'
                            }, {
                                'chunk': 'tomato\n',
                                'date': '2016-04-27T12:00:05',
                                'log_path': '/some/service.log'
                            }
                        ]
                    }
                }),
            ]
        finally:
            p.terminate()
            p.join()
