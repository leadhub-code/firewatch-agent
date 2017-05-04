from helpers import get_free_tcp_port, write_file

from firewatch_agent.configuration import AgentConfiguration
from firewatch_agent.agent import Agent


def test_overall_egent(tmp_dir):
    hub_port = get_free_tcp_port()
    agent_conf_path = write_file(tmp_dir / 'agent.yaml', '''
        firewatch_agent:
            firewatch_hub_endpoint: http://localhost:5000/firewatch-hub/
            id_file: agent_id
            state_file: state.yaml
            scan_paths: # where to look for files firewatch-logs.yaml
                - '*/log'
    ''')
    logs_conf_path = write_file(tmp_dir / 'some-service/log/firewatch-logs.yaml', '''
        firewatch_logs:
            - log_paths:
                - *.log
              error_regex: ERR
              warning_regex: WARN
              context_before: 10
              context_after: 10
              context_timeout: 0
              thread_regex: null
    ''')
    log_path = write_file(tmp_dir / 'some-service/log/some.log', '''
        cheese
        WARNING: bacon
    ''')
    agent_conf = AgentConfiguration(agent_conf_path)
    agent = Agent(agent_conf)
