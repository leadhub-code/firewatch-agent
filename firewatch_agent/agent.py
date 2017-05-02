import logging
from pathlib import Path
import yaml
from time import sleep

from .reader import Reader
from .util import unique


logger = logging.getLogger(__name__)


class Agent:

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
                        logger.debug('scan_dir: %s', pp)
                        if pp.name.startswith('.'):
                            continue
                        if pp.is_dir():
                            scan_dir(pp)
                        elif pp.is_file():
                            if pp.name == 'firewatch-logs.yaml':
                                logger.info('Processing configuration file %s', pp)
                                with pp.open() as f:
                                    data = yaml.safe_load(f)
                                cfg = data['firewatch_logs']
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
            log_path_str = str(log_path)
            for line in reader.read():
                self.listener.log_line(log_path_str, line)
        self.listener.flush()
        self.state_store.commit()

    def run_forever(self):
        while True:
            self.run_iteration()
            sleep(1)
