import logging


logger = logging.getLogger(__name__)


class Scanner:
    '''
    Scans given paths for configuration files and processes them -
    reads log files and sends log lines to line_processor.
    '''

    def __init__(self, scan_paths_patterns):
        self._scan_paths_patterns = scan_paths_patterns
