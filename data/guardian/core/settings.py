#!/usr/bin/env python3
"""Shared settings and path resolution for the Guardian skill."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "admin_override": False,
    "scan_paths": ["auto"],
    "db_path": "auto",
    "scan_interval_minutes": 2,
    "severity_threshold": "medium",
    "dismissed_signatures": [],
    "custom_definitions_dir": None,
    "channels": {
        "monitor_all": True,
        "exclude_channels": [],
    },
    "alerts": {
        "notify_on_critical": True,
        "notify_on_high": False,
        "daily_digest": True,
        "daily_digest_time": "09:00",
    },
    "admin": {
        "bypass_token": None,
        "disable_until": None,
        "trusted_sources": [],
    },
    "false_positive_suppression": {
        "min_context_words": 3,
        "suppress_assistant_number_matches": True,
        "allowlist_patterns": [],
    },
}


def resolve_workspace(cwd: Optional[Path] = None) -> Path:
    """Resolve Guardian workspace using env vars and documented fallback order."""
    guardian_workspace = os.environ.get("GUARDIAN_WORKSPACE")
    if guardian_workspace:
        return Path(guardian_workspace).expanduser().resolve()

    openclaw_workspace = os.environ.get("OPENCLAW_WORKSPACE")
    if openclaw_workspace:
        return Path(openclaw_workspace).expanduser().resolve()

    default_workspace = Path.home() / ".openclaw" / "workspace"
    if default_workspace.exists():
        return default_workspace.resolve()

    return (cwd or Path.cwd()).resolve()


def skill_root() -> Path:
    """Return the absolute root path of this Guardian skill checkout."""
    return Path(__file__).resolve().parent.parent


def definitions_dir(config: Optional[Dict[str, Any]] = None) -> Path:
    """Return definitions directory, honoring optional custom definitions path."""
    if config and config.get("custom_definitions_dir"):
        return Path(str(config["custom_definitions_dir"])).expanduser().resolve()
    return skill_root() / "definitions"


def default_db_path(workspace: Optional[Path] = None) -> Path:
    """Return default SQLite DB path for Guardian state."""
    ws = workspace or resolve_workspace()
    return ws / "guardian.db"


def _config_path(config_path: Optional[str] = None) -> Path:
    if config_path:
        return Path(config_path).expanduser().resolve()

    env_config = os.environ.get("GUARDIAN_CONFIG")
    if env_config:
        return Path(env_config).expanduser().resolve()

    return skill_root() / "config.json"


def _openclaw_config_path(workspace: Optional[Path] = None) -> Optional[Path]:
    env_cfg = os.environ.get("OPENCLAW_CONFIG_PATH")
    if env_cfg:
        return Path(env_cfg).expanduser().resolve()

    ws = workspace or resolve_workspace()
    candidates = [
        ws.parent / "openclaw.json",
        Path.home() / ".openclaw" / "openclaw.json",
        Path.cwd() / "openclaw.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def _deep_update(base: Dict[str, Any], updates: Dict[str, Any]) -> None:
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_update(base[key], value)
        else:
            base[key] = value


def _extract_guardian_config(raw: Dict[str, Any]) -> Dict[str, Any]:
    skills = raw.get("skills") if isinstance(raw, dict) else None
    cfg: Dict[str, Any] = {}
    if isinstance(skills, dict):
        guardian = skills.get("guardian", {})
        if isinstance(guardian, dict):
            candidate = guardian.get("config") or guardian.get("settings")
            if isinstance(candidate, dict):
                cfg = candidate
    elif isinstance(raw, dict):
        cfg = raw

    if not isinstance(cfg, dict):
        return {}

    # Normalize trusted_sources to admin.trusted_sources when provided at top level
    if "trusted_sources" in cfg:
        admin_cfg = cfg.get("admin") if isinstance(cfg.get("admin"), dict) else {}
        if "trusted_sources" not in admin_cfg:
            admin_cfg["trusted_sources"] = cfg.get("trusted_sources")
        cfg["admin"] = admin_cfg

    return cfg


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid Guardian config JSON: {path}") from exc
    except OSError:
        return {}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load Guardian config, preferring OpenClaw config then falling back to skill config."""
    merged: Dict[str, Any] = json.loads(json.dumps(DEFAULT_CONFIG))

    # 1) Explicit config path (can be openclaw.json or guardian config)
    if config_path:
        cfg = _extract_guardian_config(_load_json(_config_path(config_path)))
        _deep_update(merged, cfg)
        return merged

    # 2) OpenClaw config (Control UI) if present
    oc_path = _openclaw_config_path()
    if oc_path and oc_path.exists():
        cfg = _extract_guardian_config(_load_json(oc_path))
        if cfg:
            _deep_update(merged, cfg)
            return merged

    # 3) Fallback to skill config.json
    skill_cfg_path = _config_path()
    if skill_cfg_path.exists():
        cfg = _load_json(skill_cfg_path)
        _deep_update(merged, cfg)

    return merged


def resolve_scan_paths(config: Dict[str, Any]) -> List[Path]:
    """Resolve scan target paths from config with auto-discovery support."""
    raw_paths = config.get("scan_paths", ["auto"])
    if not isinstance(raw_paths, list) or not raw_paths:
        raw_paths = ["auto"]

    resolved: List[Path] = []
    for raw in raw_paths:
        if raw == "auto":
            for auto_path in [
                Path.home() / ".openclaw" / "agents",
                Path.home() / ".openclaw" / "cron",
            ]:
                if auto_path.exists():
                    resolved.append(auto_path)
        else:
            candidate = Path(str(raw)).expanduser().resolve()
            if candidate.exists():
                resolved.append(candidate)

    deduped: List[Path] = []
    seen = set()
    for item in resolved:
        normalized = str(item)
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(item)

    return deduped


def severity_min_score(level: str) -> int:
    """Convert severity threshold label to a minimum numeric score."""
    mapping = {
        "low": 0,
        "medium": 50,
        "high": 80,
        "critical": 90,
    }
    return mapping.get(str(level).lower(), 50)
