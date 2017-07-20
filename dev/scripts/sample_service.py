#!/usr/bin/env python3

import argparse
import logging
from random import random, choice
from time import sleep


logger = logging.getLogger(__name__)

default_log_path = 'sample_service.log'

fmt = '%(asctime)s %(levelname)7s: %(message)s'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--log')
    args = p.parse_args()
    setup_logging(args.log or default_log_path)

    while True:
        logger.info(choice(words))
        if random() < .3:
            logger.warning(choice(words))
        if random() < .1:
            logger.error(choice(words))
        sleep(random())


words = '''
    banana bacon cheese apple orange chocolate beer potato curry cucumber onion pear
'''.split()


def setup_logging(log_path):
    from logging import Formatter
    from logging.handlers import WatchedFileHandler

    logging.basicConfig(format=fmt, level=logging.DEBUG)

    h = WatchedFileHandler(log_path)
    h.setFormatter(Formatter(fmt))
    h.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(h)


if __name__ == '__main__':
    main()
