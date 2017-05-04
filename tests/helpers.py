import socket
from textwrap import dedent


def write_file(path, content):
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)
    with path.open('w') as f:
        f.write(dedent(content))
    return path


def get_free_tcp_port(start=9901):
    '''
    Used in tests
    '''
    port = start
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', port))
        finally:
            s.close()
        return port
        port += 1
