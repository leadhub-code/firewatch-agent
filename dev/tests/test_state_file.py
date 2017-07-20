from textwrap import dedent

from firewatch_agent.state_file import StateFile


def test_state_file_empty(tmp_dir):
    p = tmp_dir / 'state.json'
    sf = StateFile(p)
    sf.save()
    assert p.read_text() == dedent('''\
        {
          "firewatch_agent_state": {}
        }
    ''')
