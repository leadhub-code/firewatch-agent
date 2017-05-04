from helpers import get_free_tcp_port


def test_get_free_tcp_port():
    port = get_free_tcp_port()
    assert isinstance(port, int)
