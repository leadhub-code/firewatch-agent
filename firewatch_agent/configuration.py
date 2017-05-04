import logging
import yaml


logger = logging.getLogger(__name__)


default_id_file_path = '/etc/firewatch/agent_id'
default_state_file_path = '/var/lib/firewatch-agent/state.yaml'


class AgentConfiguration:

    def __init__(self, cfg_path):
        with cfg_path.open() as f:
            data = yaml.safe_load(f)
        cfg = data['firewatch_agent']
        cfg_dir = cfg_path.parent.resolve()
        self.firewatch_hub_endpoint = cfg['firewatch_hub_endpoint']
        if cfg.get('id_file'):
            self.id_file_path = cfg_dir / cfg['id_file']
        else:
            self.id_file_path = default_id_file_path
        if cfg.get('state_file'):
            self.state_file_path = cfg_dir / cfg['state_file']
        else:
            self.state_file_path = default_state_file_path
        self.scan_paths = [cfg_dir / p for p in cfg['scan_paths']]


class LogsConfiguration:

    def __init__(self, cfg_path):
        with cfg_path.open() as f:
            data = yaml.safe_load(f)
        cfg = data['firewatch_logs']
        cfg_dir = cfg_path.parent.resolve()
        self.log_paths = []
        for p in cfg['log_paths']:
            for lp in cfg_dir.glob(p):
                self.log_paths.append(lp)
        # TODO: add other configuration options
