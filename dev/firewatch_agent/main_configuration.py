from pathlib import Path
import yaml


class MainConfiguration:

    def __init__(self):
        self.main_conf_path = None
        self.log_file_path = None
        self.state_file_path = None
        self.token_file_path = None
        self.report_url = None
        self.scan_paths = None
        self.source_conf_name = None
        self.default_source_conf_name = 'firewatch-agent-source.yaml'

    def load_from_file(self, cfg_path):
        self.main_conf_path = cfg_path = cfg_path.resolve()
        cfg_dir = cfg_path.parent
        cfg = yaml.safe_load(cfg_path.read_text())['firewatch_agent_main']
        if cfg.get('log_file'):
            self.log_file_path = cfg_dir / cfg['log_file']
        if cfg.get('state_file'):
            self.state_file_path = cfg_dir / cfg['state_file']
        if cfg.get('report_url'):
            self.report_url = cfg['report_url']
        if cfg.get('scan_paths'):
            if not isinstance(cfg['scan_paths'], list):
                raise Exception('Value scan_paths must be a list in {}'.format(cfg_path))
            self.scan_paths = [(cfg_dir / p).resolve() for p in cfg['scan_paths']]
        if cfg.get('source_conf_name'):
            self.source_conf_name = cfg['source_conf_name']

    def load_from_args(self, args):
        if args.log:
            self.log_file_path = Path(args.log)
        if args.state:
            self.state_file_path = Path(args.state)
        if args.token:
            self.token_file_path = Path(args.token)
        if args.report:
            self.report_url = Path(args.report)
        if args.scan:
            self.scan_paths = [Path(p).resolve() for p in args.scan]
        if args.source_conf_name:
            self.source_conf_name = source_conf_name
