import logging
from pathlib import Path


logging.basicConfig(
    format='> %(asctime)s %(name)s %(levelname)5s: %(message)s',
    level=logging.DEBUG)


def tmp_dir(tmpdir):
    return Path(str(tmpdir))
