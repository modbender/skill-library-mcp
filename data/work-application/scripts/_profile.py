"""
_profile.py - Profile management for the work-application skill.
Handles loading/saving master and adapted profiles. Stdlib only.

Storage is delegated to _storage.py (local or Nextcloud).
Config is always local:  ~/.openclaw/config/work-application/config.json

Usage:
    from _profile import load_master_profile, load_adapted_profile, save_adapted_profile
"""

import json
from pathlib import Path

# ── Paths (config is always local) ───────────────────────────────────────────
_DATA_DIR   = Path.home() / ".openclaw" / "data" / "work-application"
_CONFIG_DIR = Path.home() / ".openclaw" / "config" / "work-application"

MASTER_PROFILE_FILE  = _DATA_DIR / "profile-master.json"
ADAPTED_PROFILE_FILE = _DATA_DIR / "profile.json"
CONFIG_FILE          = _CONFIG_DIR / "config.json"

# File names used as storage keys
_MASTER_NAME  = "profile-master.json"
_ADAPTED_NAME = "profile.json"

_DEFAULT_CONFIG = {
    "allow_write": False,
    "allow_export": True,
    "allow_scrape": False,
    "allow_tracking": True,
    "default_template": "classic",
    "default_color": "#2563eb",
    "default_lang": "fr",
    "readonly_mode": False,
    "storage": {
        "backend": "local",
        "path": "/OpenClaw/work-application",
    },
    "scraper": {
        "searches": [],
        "filters": {
            "excludeCompanies": [],
            "minTJM": 500,
            "minSalary": 60000,
            "maxAge": 4,
            "locations": [],
            "excludeLocations": [],
        },
        "rate_limit_ms": 2000,
        "scroll_timeout_ms": 5000,
    },
}


class ProfileError(Exception):
    """Raised when a profile operation fails."""


# ── Storage helper ───────────────────────────────────────────────────────────

def _store():
    """Return the configured storage backend."""
    from _storage import get_storage
    return get_storage()


# ── Config (always local) ───────────────────────────────────────────────────

def load_config() -> dict:
    """Load config from disk, merging with defaults."""
    cfg = dict(_DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            # Deep merge scraper section
            if "scraper" in data and "scraper" in cfg:
                scraper_defaults = dict(cfg["scraper"])
                scraper_defaults.update(data.pop("scraper"))
                cfg.update(data)
                cfg["scraper"] = scraper_defaults
            else:
                cfg.update(data)
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


def save_config(cfg: dict) -> None:
    """Write config to disk."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# ── Permissions ──────────────────────────────────────────────────────────────

def _check_permission(cfg: dict, action: str) -> None:
    """Raise ProfileError if action is not permitted."""
    if cfg.get("readonly_mode", False):
        raise ProfileError("readonly_mode is enabled - all writes are blocked")
    if not cfg.get(action, False):
        raise ProfileError(f"Permission denied: {action}=false in config")


# ── Profile operations ───────────────────────────────────────────────────────

def load_master_profile() -> dict:
    """Load the master profile from storage."""
    store = _store()
    if not store.exists(_MASTER_NAME):
        raise ProfileError(
            f"Master profile not found.\n"
            "  Run setup.py first: python3 scripts/setup.py"
        )
    try:
        return store.read_json(_MASTER_NAME)
    except Exception as e:
        raise ProfileError(f"Failed to load master profile: {e}")


def load_adapted_profile() -> dict:
    """Load the adapted (current) profile from storage."""
    store = _store()
    if not store.exists(_ADAPTED_NAME):
        raise ProfileError(
            f"Adapted profile not found.\n"
            "  Generate one by adapting the master profile for a job offer."
        )
    try:
        return store.read_json(_ADAPTED_NAME)
    except Exception as e:
        raise ProfileError(f"Failed to load adapted profile: {e}")


def save_adapted_profile(profile: dict, cfg: dict = None) -> None:
    """Save the adapted profile. Requires allow_write permission."""
    if cfg is None:
        cfg = load_config()
    _check_permission(cfg, "allow_write")
    store = _store()
    store.ensure_dir()
    store.write_json(_ADAPTED_NAME, profile)


def update_master_profile(data: dict, cfg: dict = None) -> None:
    """Update fields in the master profile. Requires allow_write permission."""
    if cfg is None:
        cfg = load_config()
    _check_permission(cfg, "allow_write")
    master = load_master_profile()
    master.update(data)
    store = _store()
    store.ensure_dir()
    store.write_json(_MASTER_NAME, master)


def profile_exists(path=None) -> dict | bool:
    """Check which profile files exist.

    If path is given (legacy), return bool for that specific path.
    Otherwise return {master: bool, adapted: bool, config: bool}.
    """
    if path is not None:
        # Legacy call from init.py: profile_exists(MASTER_PROFILE_FILE)
        store = _store()
        name = Path(path).name
        if name in (_MASTER_NAME, _ADAPTED_NAME):
            return store.exists(name)
        return Path(path).exists()

    store = _store()
    return {
        "master": store.exists(_MASTER_NAME),
        "adapted": store.exists(_ADAPTED_NAME),
        "config": CONFIG_FILE.exists(),
    }
