import logging
from pathlib import Path
from pytest import fixture


logging.basicConfig(
    format='> %(asctime)s %(name)s %(levelname)5s: %(message)s',
    level=logging.DEBUG)


@fixture
def tmp_dir(tmpdir):
    return Path(str(tmpdir))
