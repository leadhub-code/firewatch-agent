from collections import deque
from fnmatch import fnmatchcase
import logging
import os
from pathlib import Path
from stat import S_ISDIR, S_ISREG
from time import sleep
from time import monotonic as monotime
import yaml


logger = logging.getLogger(__name__)


class Firewatch:

    sleep_interval = 1
    scan_interval = 5

    def __init__(self, main_conf):
        self.main_conf = main_conf
        self.last_scanned = None
        self.heads = {} # (path, inode) -> Head

    def run_forever(self):
        while True:
            logger.debug('main loop iteration')
            self._scan()
            for k, head in self.heads.items():
                head.run()
            sleep(self.sleep_interval)

    def _scan(self):
        now = monotime()
        if self.last_scanned is not None and self.last_scanned > (now - self.scan_interval):
            return
        logger.debug('scanning')
        present = set()
        for src_conf_path in self._find_potential_src_conf_paths():
            logger.debug('Processing src conf: %s', src_conf_path)
            src_conf, err = self._try_load_src_conf(src_conf_path)
            if not src_conf:
                logger.info('Failed to load src conf: %s - %s', src_conf_path, err)
                continue
            assert not err
            for log_path, log_conf in self._find_log_files(src_conf):
                logger.debug('Found log file: %s', log_path)
                log_stat = log_path.stat()
                log_inode = log_stat.st_ino
                if (log_path, log_inode) not in self.heads:
                    h = Head(log_path, log_conf)
                    # Get inode again from the opened file so there is no
                    # race condition between stat() and open().
                    log_inode = h.get_inode()
                    self.heads[(log_path, log_inode)] = h
                present.add((log_path, log_inode))

        for k, head in self.heads.items():
            if k not in present:
                head.unlinked()

        self.last_scanned = now
        logger.debug(
            'Scan done in %.3f s; heads: %s',
            monotime() - now,
            ', '.join(str(k) for k in self.heads.keys()) or '-')

    def _find_potential_src_conf_paths(self):
        assert self.main_conf.main_conf_path or self.main_conf.scan_paths
        if self.main_conf.main_conf_path:
            yield self.main_conf.main_conf_path
        if self.main_conf.scan_paths:
            src_conf_name = self.main_conf.source_conf_name or self.main_conf.default_source_conf_name
            assert src_conf_name
            scanned_dirs = set()
            for p in self.main_conf.scan_paths:
                assert isinstance(p, Path)
                yield from self._scan_for_src_conf_files(p, src_conf_name, scanned_dirs)

    def _scan_for_src_conf_files(self, dir_path, src_conf_name, scanned_dirs):
        '''
        Called from _find_potential_src_conf_paths()
        '''
        if dir_path in scanned_dirs:
            return
        scanned_dirs.add(dir_path)
        logger.debug('Searching src conf files in %s', dir_path)
        size_limit = 2**20
        for p in sorted(dir_path.iterdir(), key=str):
            p_st = p.stat()
            if S_ISDIR(p_st.st_mode):
                yield from self._scan_for_src_conf_files(p, src_conf_name, scanned_dirs)
            elif S_ISREG(p_st.st_mode):
                if p_st.st_size < size_limit and fnmatchcase(p.name, src_conf_name):
                    yield p.resolve()

    def _try_load_src_conf(self, src_conf_path):
        content = src_conf_path.read_text()
        assert callable(yaml.safe_load)
        try:
            parsed = yaml.safe_load(content)
            if 'firewatch_agent_source' not in parsed:
                return None, 'top-level key firewatch_agent_source'
            src_conf = SourceConfiguration(src_conf_path, parsed['firewatch_agent_source'])
            return src_conf, None
        except Exception as e:
            return None, repr(e)

    def _find_log_files(self, src_conf):
        assert isinstance(src_conf, SourceConfiguration)
        for log_conf in src_conf.logs:
            assert isinstance(log_conf, SourceLogConfiguration)
            if not log_conf.filename_patterns:
                logger.info('No filename patterns configured in %s', log_conf)
                continue
            if not log_conf.error_regexes and not log_conf.warning_regexes:
                logger.info('No error/warning regexes configured in %s', log_conf)
                continue
            for dir_path in log_conf.dir_paths:
                assert isinstance(dir_path, Path)
                for p in sorted(dir_path.iterdir(), key=str):
                    matches = any(fnmatchcase(p.name, pat) for pat in log_conf.filename_patterns)
                    if matches:
                        if not p.is_file():
                            logger.info('Path %s matches, but is not a file'. p)
                        else:
                            yield p, log_conf


class SourceConfiguration:

    def __init__(self, cfg_path, cfg):
        self.logs = []
        if cfg.get('logs'):
            if not isinstance(cfg['logs'], list):
                raise Exception('Value "logs" must be list in {}'.format(cfg_path))
            for n, log in enumerate(cfg['logs']):
                if not isinstance(log, dict):
                    raise Exception('Value "logs[{}]" must be dict in {}'.format(n, cfg_path))
                self.logs.append(SourceLogConfiguration(cfg_path, log))


class SourceLogConfiguration:

    def __init__(self, cfg_path, log_cfg):
        cfg_dir = cfg_path.parent
        self.dir_paths = []
        self.filename_patterns = []
        self.error_regexes = []
        self.warning_regexes = []
        self.false_positive_regexes = []

        if log_cfg.get('directory'):
            if isinstance(log_cfg['directory'], str):
                self.dir_paths.append(cfg_dir / log_cfg['directory'])
            elif isinstance(log_cfg['directory'], list):
                for p in log_cfg['directory']:
                    if not isinstance(p, str):
                        raise Exception('directory must be a string: {!r}'.format(p))
                    self.dir_paths.append(cfg_dir / p)
            else:
                raise Exception('Value of directory must be str or list, not {!r}'.format(log_cfg['path']))

        if not self.dir_paths:
            self.dir_paths.append(cfg_dir)

        if isinstance(log_cfg['filename'], str):
            self.filename_patterns.append(log_cfg['filename'])
        elif isinstance(log_cfg['filename'], list):
            for p in log_cfg['filename']:
                if not isinstance(p, str):
                    raise Exception('filename must be str: {!r}'.format(p))
                self.filename_patterns.append(p)

        if not self.filename_patterns:
            raise Exception('No filename patterns defined')

        if log_cfg.get('error_regex'):
            if isinstance(log_cfg['error_regex'], str):
                self.error_regexes.append(log_cfg['error_regex'])
            elif isinstance(log_cfg['error_regex'], list):
                for expr in log_cfg['error_regex']:
                    self.error_regexes.append(expr)

        if log_cfg.get('warning_regex'):
            if isinstance(log_cfg['warning_regex'], str):
                self.warning_regexes.append(log_cfg['warning_regex'])
            elif isinstance(log_cfg['warning_regex'], list):
                for expr in log_cfg['warning_regex']:
                    self.warning_regexes.append(expr)

        if log_cfg.get('false_positive_regex'):
            if isinstance(log_cfg['false_positive_regex'], str):
                self.false_positive_regexes.append(log_cfg['false_positive_regex'])
            elif isinstance(log_cfg['false_positive_regex'], list):
                for expr in log_cfg['false_positive_regex']:
                    self.false_positive_regexes.append(expr)


class Head:

    def __init__(self, log_path, log_conf):
        self.log_path = log_path
        self.log_conf = log_conf
        self.stream = log_path.open('rb')
        self.last_lines = deque(maxlen=100)
        self.interest_lines = None
        self.interest_deadline = None
        self.interest_context = 0

    def get_inode(self):
        return os.stat(self.stream.fileno()).st_ino

    def run(self):
        while True:
            line = self.stream.readline()
            if not line:
                break
            logger.debug('%s line: %r', self.log_path, line)
