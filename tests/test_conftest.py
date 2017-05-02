from datetime import datetime


def test_system_add_time(system, add_time):
    dt = lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    assert system.utcnow() == dt('2017-04-27 12:00:00')
    add_time(minutes=1, seconds=5)
    assert system.utcnow() == dt('2017-04-27 12:01:05')
