#!/usr/bin/env python3
"""Shared storage helpers for the Tesla Fleet API skill.

State lives in the workspace: {workspace}/tesla-fleet-api/

Files:
  - config.json   (configuration + provider creds)
  - auth.json     (OAuth tokens)
  - vehicles.json (cached vehicle list)
  - places.json   (named lat/lon places)

Auth: set TESLA_CLIENT_ID / TESLA_CLIENT_SECRET in the environment,
or put them in config.json (keys: "client_id", "client_secret").

This module is stdlib-only and safe to import from any of the scripts.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


def _find_workspace_root() -> str:
    """Resolve the OpenClaw workspace root.

    Priority: OPENCLAW_WORKSPACE env → walk up from __file__ looking for
    SOUL.md / AGENTS.md → fallback to ~/.openclaw.
    """
    env_ws = os.environ.get("OPENCLAW_WORKSPACE")
    if env_ws and os.path.isdir(env_ws):
        return env_ws

    # Walk up from CWD
    cwd = os.getcwd()
    d = cwd
    for _ in range(10):
        if os.path.exists(os.path.join(d, "SOUL.md")) or os.path.exists(
            os.path.join(d, "AGENTS.md")
        ):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent

    # Walk up from this script's location (follows symlinks)
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.exists(os.path.join(d, "SOUL.md")) or os.path.exists(
            os.path.join(d, "AGENTS.md")
        ):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent

    return os.path.expanduser("~/.openclaw")


def default_dir() -> str:
    """Default state directory: {workspace}/tesla-fleet-api/.

    Falls back to ~/.openclaw/tesla-fleet-api if workspace detection fails.
    """
    ws = _find_workspace_root()
    return os.path.join(ws, "tesla-fleet-api")


def config_path(dir_path: str) -> str:
    return os.path.join(dir_path, "config.json")


def auth_path(dir_path: str) -> str:
    return os.path.join(dir_path, "auth.json")


def vehicles_path(dir_path: str) -> str:
    return os.path.join(dir_path, "vehicles.json")


def places_path(dir_path: str) -> str:
    return os.path.join(dir_path, "places.json")


def _mkdirp(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_env_file(dir_path: str) -> None:
    """Load provider creds from config.json into os.environ.

    Maps config.json keys to environment variables:
      client_id       -> TESLA_CLIENT_ID
      client_secret   -> TESLA_CLIENT_SECRET
      audience        -> TESLA_AUDIENCE

    Existing env vars are NOT overwritten.
    """
    cfg = get_config(dir_path)
    _env_map = {
        "client_id": "TESLA_CLIENT_ID",
        "client_secret": "TESLA_CLIENT_SECRET",
        "audience": "TESLA_AUDIENCE",
    }
    for cfg_key, env_key in _env_map.items():
        val = cfg.get(cfg_key)
        if val and env_key not in os.environ:
            os.environ[env_key] = str(val)


def read_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def write_json_private(path: str, obj: Dict[str, Any]) -> None:
    parent = os.path.dirname(path)
    if parent:
        _mkdirp(parent)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")
    try:
        os.chmod(tmp, 0o600)
    except Exception:
        pass
    os.replace(tmp, path)


def get_config(dir_path: str) -> Dict[str, Any]:
    return read_json(config_path(dir_path))


def save_config(dir_path: str, cfg: Dict[str, Any]) -> None:
    write_json_private(config_path(dir_path), cfg)


def get_auth(dir_path: str) -> Dict[str, Any]:
    return read_json(auth_path(dir_path))


def save_auth(dir_path: str, auth: Dict[str, Any]) -> None:
    write_json_private(auth_path(dir_path), auth)


def get_vehicles(dir_path: str) -> Dict[str, Any]:
    return read_json(vehicles_path(dir_path))


def save_vehicles(dir_path: str, data: Dict[str, Any]) -> None:
    write_json_private(vehicles_path(dir_path), data)


def get_places(dir_path: str) -> Dict[str, Any]:
    return read_json(places_path(dir_path))


def save_places(dir_path: str, data: Dict[str, Any]) -> None:
    write_json_private(places_path(dir_path), data)


def env(name: str) -> Optional[str]:
    v = os.environ.get(name)
    return v if v not in (None, "") else None
