import flask
import logging
import multiprocessing
from pprint import pprint
import requests
from textwrap import dedent
from time import sleep

from firewatch_agent.agent import Agent
from firewatch_agent.collector import Collector
from firewatch_agent.report_listener import ReportWarningListener
from firewatch_agent.state_store import YAMLStateStore

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


def test_integration(tmp_dir, system):
    port = get_free_tcp_port()
    base_url = 'http://127.0.0.1:{}'.format(port)
    report_url = base_url + '/report'
    state_path = tmp_dir / 'state.yaml'
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
        f.write('ERROR: tomato\n')
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
            state_store = YAMLStateStore(state_path)
            report_listener = ReportWarningListener(report_url, agent_id='A1', system=system)
            collector = Collector(report_listener, system=system)
            agent = Agent(
                scan_paths=[tmp_dir],
                state_store=state_store,
                listener=collector)
            agent.run_iteration()
            try:
                assert list(received) == [
                    ('report', {
                        'firewatch_report': {
                            'agent_id': 'A1',
                            'host': 'server.example.com',
                            'events': [
                                {
                                    'chunk': 'ERROR: tomato\n',
                                    'date': '2017-04-27T12:00:00',
                                    'log_path': str(log_file),
                                }
                            ]
                        }
                    }),
                ]
            except:
                pprint(list(received))
                raise
        finally:
            p.terminate()
            p.join()
            logger.debug('Test server process finished: %s', p)
