import argparse
import logging
from pathlib import Path
import sys

from .firewatch import Firewatch
from .main_configuration import MainConfiguration


logger = logging.getLogger(__name__)

github_url = 'https://github.com/leadhub-code/firewatch-agent'


def agent_main():
    p = argparse.ArgumentParser(
        description='Watch log files for errors and warnings. See ' + github_url,
        formatter_class=CustomHelpFormatter)
    p.add_argument('--verbose', '-v', action='store_true', help='more logging'),
    p.add_argument('--conf', metavar='FILE', help='path to main configuration file')
    p.add_argument('--log', metavar='FILE', help='where to log')
    p.add_argument('--state', metavar='FILE', help='path to file to store the agent state')
    p.add_argument('--token', metavar='FILE', help='path to file with secret token')
    p.add_argument('--report', metavar='URL', help='Firewatch Hub report URL')
    p.add_argument('--scan', metavar='DIR', action='append', help='where to search for source configuration files')
    p.add_argument('--source-conf-name', metavar='FILENAME',
        help='source configuration name to look for while searching the scan paths')
    args = p.parse_args()
    setup_logging(args.verbose)
    try:
        main_conf = MainConfiguration()
        if args.conf:
            main_conf.load_from_file(Path(args.conf))
        main_conf.load_from_args(args)
        if main_conf.log_file_path:
            log_to_file(main_conf.log_file_path, verbose)
        Firewatch(main_conf).run_forever()
    except Exception as e:
        logger.exception('Firewatch Agent failed: %r', e)
        sys.exit(1)


class CustomHelpFormatter (argparse.HelpFormatter):

    def __init__(self, **kwargs):
        kwargs = dict(kwargs, max_help_position=31, width=100)
        super().__init__(**kwargs)


log_format = '%(asctime)s [%(process)d] %(name)-25s %(levelname)5s: %(message)s'


def setup_logging(verbose):
    from logging import DEBUG, INFO, WARNING, Formatter, StreamHandler

    logging.getLogger('').setLevel(DEBUG)

    h = StreamHandler()
    h.setFormatter(Formatter(log_format))
    h.setLevel(DEBUG if verbose else WARNING)
    logging.getLogger('').addHandler(h)


def log_to_file(log_path, verbose):
    from logging import DEBUG, INFO, Formatter
    from logging.handlers import WatchedFileHandler

    h = WatchedFileHandler(str(log_path))
    h.setFormatter(Formatter(log_format))
    h.setLevel(DEBUG if verbose else INFO)
    logging.getLogger('').addHandler(h)
