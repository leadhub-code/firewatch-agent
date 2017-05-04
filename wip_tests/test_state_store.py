import yaml

from firewatch_agent.state_store import YAMLStateStore


def test_yaml_state_store(tmp_dir):
    state_path = tmp_dir / 'state.ymal'
    store = YAMLStateStore(state_path)
    assert store.get('foo') is None
    store.update('foo', {'bar': 42})
    assert store.get('foo') == {'bar': 42}
    store.commit()
    store = YAMLStateStore(state_path)
    assert store.get('foo') == {'bar': 42}
    data = yaml.load(state_path.open())
    assert data == {'firewatch_agent_states': {'foo': {'bar': 42}}}
