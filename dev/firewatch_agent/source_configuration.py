import logging
import re


logger = logging.getLogger(__name__)


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
                self.error_regexes.append(re.compile(log_cfg['error_regex']))
            elif isinstance(log_cfg['error_regex'], list):
                for expr in log_cfg['error_regex']:
                    assert isinstance(expr, str)
                    self.error_regexes.append(re.compile(expr))

        if log_cfg.get('warning_regex'):
            if isinstance(log_cfg['warning_regex'], str):
                self.warning_regexes.append(re.compile(log_cfg['warning_regex']))
            elif isinstance(log_cfg['warning_regex'], list):
                for expr in log_cfg['warning_regex']:
                    assert isinstance(expr, str)
                    self.warning_regexes.append(re.compile(expr))

        if log_cfg.get('false_positive_regex'):
            if isinstance(log_cfg['false_positive_regex'], str):
                self.false_positive_regexes.append(re.compile(log_cfg['false_positive_regex']))
            elif isinstance(log_cfg['false_positive_regex'], list):
                for expr in log_cfg['false_positive_regex']:
                    assert isinstance(expr, str)
                    self.false_positive_regexes.append(re.compile(expr))
