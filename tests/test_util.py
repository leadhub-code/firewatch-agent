from firewatch_agent.util import unique


def test_unique_with_iterator():
    assert unique(iter('qwerq')) == ['q', 'w', 'e', 'r']
