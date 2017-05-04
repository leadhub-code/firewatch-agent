import logging
from pathlib import Path
import yaml
from time import sleep

from .reader import Reader
from .util import unique


logger = logging.getLogger(__name__)


class Agent:
    '''
    Connects all pieces (Scanner, LineProcessor, ...) together.
    Called from main() and from integration tests.
    '''

    def __init__(self, agent_conf):
        self.scanner = Scanner(agent_conf.scan_paths)

    def run_forever(self):
        assert 0, 'NIY'

    def run_iteration(self):
        pass


class XXXAgent:

    def __init__(self, scan_paths, state_store, listener):
        self.scan_paths = [Path(p) for p in scan_paths]
        self.state_store = state_store
        self.listener = listener

    def run_iteration(self):
        # TODO: rewrite :)
        logger.debug('iteration')
        log_paths = []
        for p in self.scan_paths:
            if p.is_dir():
                logger.info('Scanning directory %s', p)
                def scan_dir(p):
                    for pp in p.iterdir():
                        if pp.name.startswith('.'):
                            continue
                        if pp.is_dir():
                            scan_dir(pp)
                        elif pp.is_file():
                            if pp.name == 'firewatch-agent.yaml':
                                logger.info('Processing configuration file %s', pp)
                                with pp.open() as f:
                                    data = yaml.safe_load(f)
                                cfg = data['firewatch_agent']
                                cfg_dir = pp.parent
                                logger.debug('cfg: %r', cfg)
                                for pattern in cfg['log_files']:
                                    x_log_paths = list(cfg_dir.glob(pattern))
                                    x_log_paths.sort(key=str)
                                    logger.debug('%s -> %s', pattern, ' '.join(str(p) for p in x_log_paths))
                                    log_paths.extend(x_log_paths)
                scan_dir(p)
        log_paths = unique(log_paths)
        logger.debug('All log paths: %s', ' '.join(str(p) for p in log_paths))
        for log_path in log_paths:
            reader = Reader(log_path, self.state_store)
            for line in reader.read():
                self.listener.log_line(log_path, line)
        self.listener.flush()

    def run_forever(self):
        while True:
            self.run_iteration()
            sleep(1)


# this is the first prototype: (TODO: review and remove)
# class Agent:
#
#     def __init__(self, agent_id, scan_path):
#         assert isinstance(agent_id, str)
#         assert isinstance(scan_path, Path)
#         self.agent_id = agent_id
#         self.scan_path = scan_path
#         self.configurations = {}
#
#     def run_forever(self):
#         logger.info('Starting; %s', self.scan_path)
#         if scan_path.is_file():
#             cfg_paths = [scan_path]
#         else:
#             cfg_paths = list(self.find_configuration_files())
#         for cfg_path in cfg_paths:
#             self.process_configuration(cfg_path)
#
#     def find_configuration_files(self, path):
#         for p in path.iterdir():
#             if p.name.startswith('.'):
#                 continue
#             if p.is_dir():
#                 yield from self.find_configuration_files(path)
#             elif p.is_file():
#                 if p.name == 'firewatch-agent.yaml':
#                     yield p
#
#     def process_configuration_file(self, cfg_path):
#         conf = Configuration(cfg_path)
#         paths = []
#         for pattern in conf.log_file_patterns:
#             paths.extend(cfg_path.glob(pattern))
#         paths = unique(paths)
#         assert 0, paths
#
#
# class Configuration:
#
#     def __init__(self, cfg_path):
#         with cfg_path.open() as f:
#             data = yaml.safe_load(f)
#         cfg = data['firewatch_agent']
#         self.log_file_patterns = cfg['log_files']
#         if not isinstance(self.log_file_patterns, list):
#             raise Exception('Exptected log_files to be list')
