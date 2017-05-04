import argparse
import logging
from pathlib import Path

from .agent import Agent
from .util import System
from .state_store import YAMLStateStore
from .report_listener import ReportWarningListener
from .collector import Collector


version = '0.0.1'

logger = logging.getLogger(__name__)


default_id_path = '/etc/firewatch/agent_id'
default_state_path = '/var/lib/firewatch-agent/state.yaml'


def agent_main():
    p = argparse.ArgumentParser()
    p.add_argument('--version', action='version', version='firewatch-agent {}'.format(version))
    p.add_argument('--verbose', '-v', action='count')
    p.add_argument('--id-file', metavar='FILE',
        help='path to file that contains agent id, will be created if not '
             'present; default: {}'.format(default_id_path))
    p.add_argument('--state', metavar='FILE',
        help='path to state file; default: {}'.format(default_state_path))
    p.add_argument('report_url')
    p.add_argument('path',
        help='path to configuration file, or directory to scan for '
             'configuration files')
    args = p.parse_args()
    setup_logging(verbosity=args.verbose)
    id_path = Path(args.id_file or default_id_path)
    agent_id = get_agent_id(id_path)
    system = System()
    state_store = YAMLStateStore(Path(args.state))
    report_listener = ReportWarningListener(args.report_url, agent_id, system=system)
    collector = Collector(report_listener, system=system)
    agent = Agent(
        scan_paths=[Path(args.path).resolve()],
        state_store=state_store,
        listener=collector)
    agent.run_forever()


def setup_logging(verbosity):
    if not verbosity:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    else:
        raise Exception('Unexpected verbosity value {!r}'.format(verbosity))
    logging.basicConfig(
        format='%(asctime)s %(name)-30s %(levelname)5s: %(message)s',
        level=level)


def get_agent_id(id_path):
    agent_id = None
    if id_path.exists():
        agent_id = read_agent_id_from_file(id_path)
    if not agent_id:
        agent_id = generate_random_agent_id()
        with id_path.open('a') as f:
            f.write('{}\n'.format(agent_id))
        check = read_agent_id_from_file(id_path)
        if check != agent_id:
            raise Exception('Failed to write agent id to {}'.format(id_path))
    assert isinstance(agent_id, str)
    assert agent_id != 'None' # :)
    return agent_id


def read_agent_id_from_file(id_path):
    with id_path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            return line
    return None


def generate_random_agent_id():
    from base64 import b64encode
    from uuid import uuid4
    return b64encode(bytes.fromhex(uuid4().hex), b'xX').rstrip(b'=').decode()
