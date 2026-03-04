"""Read API keys and skill config from openclaw.json."""

import json
import os

_CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")
_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_config_cache = None

_KEY_MAP = {
    "finnhubApiKey": "FINNHUB_API_KEY",
    "alphaVantageApiKey": "ALPHA_VANTAGE_API_KEY",
    "fredApiKey": "FRED_API_KEY",
    "fmpApiKey": "FMP_API_KEY",
    "exchangeRateApiKey": "EXCHANGE_RATE_API_KEY",
}


def _load_config():
    global _config_cache
    if _config_cache is None:
        with open(_CONFIG_PATH) as f:
            _config_cache = json.load(f)
    return _config_cache


def get_skill_config() -> dict:
    """Get config for finclaw from skills.entries.finclaw."""
    cfg = _load_config()
    return cfg.get("skills", {}).get("entries", {}).get("finclaw", {})


def get_api_key(key_name: str) -> str:
    """Get an API key from skill config env. Returns empty string if not set."""
    env = get_skill_config().get("env", {})
    env_name = _KEY_MAP.get(key_name, key_name)
    return env.get(env_name, "") or env.get(key_name, "")


def get_db_path() -> str:
    """Get the database path (inside skill directory)."""
    return os.path.join(_SKILL_DIR, "data", "finance.db")


def get_skill_dir() -> str:
    """Get the skill base directory."""
    return _SKILL_DIR
