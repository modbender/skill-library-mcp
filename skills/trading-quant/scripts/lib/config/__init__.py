import os
import yaml
from pathlib import Path

_config = None


def get_config() -> dict:
    global _config
    if _config is None:
        config_path = Path(__file__).parent / "settings.yaml"
        with open(config_path, "r") as f:
            _config = yaml.safe_load(f)
    return _config


def reload_config():
    global _config
    _config = None
    return get_config()


def get_workspace_root() -> Path:
    return Path(os.environ.get(
        "TRADING_WORKSPACE",
        os.path.expanduser("~/.openclaw/workspace-trading")
    ))
