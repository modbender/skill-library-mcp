"""Update checker — ping PyPI for newer beacon-skill releases.

Periodically queries the PyPI JSON API and compares semver tuples.
Supports automatic upgrade, dry-run, and per-version dismiss so agents
can silence notifications they've already seen.

Beacon 2.7.0 — Elyan Labs.
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests

from . import __version__
from .storage import read_json, write_json

PYPI_URL = "https://pypi.org/pypi/beacon-skill/json"
STATE_FILE = "update_state.json"
MIN_CHECK_INTERVAL = 3600  # Never check more than once per hour


def _parse_version(v: str) -> Tuple[int, ...]:
    """Parse a version string like '2.7.0' into (2, 7, 0)."""
    parts = []
    for seg in v.strip().split("."):
        try:
            parts.append(int(seg))
        except ValueError:
            break
    return tuple(parts) or (0,)


def _is_newer(latest: str, current: str) -> bool:
    """Return True if *latest* is strictly newer than *current*."""
    return _parse_version(latest) > _parse_version(current)


class UpdateManager:
    """Check PyPI for newer beacon-skill versions."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {}
        self._ucfg = self._config.get("update", {})

    # ── Config helpers ──

    def _check_enabled(self) -> bool:
        return bool(self._ucfg.get("check_enabled", True))

    def _check_interval(self) -> int:
        return max(int(self._ucfg.get("check_interval_s", 21600)), MIN_CHECK_INTERVAL)

    def _auto_upgrade(self) -> bool:
        return bool(self._ucfg.get("auto_upgrade", False))

    def _notify_in_loop(self) -> bool:
        return bool(self._ucfg.get("notify_in_loop", True))

    # ── State persistence ──

    def _load_state(self) -> Dict[str, Any]:
        return read_json(STATE_FILE)

    def _save_state(self, state: Dict[str, Any]) -> None:
        write_json(STATE_FILE, state)

    # ── Should we check now? ──

    def should_check(self) -> bool:
        """Return True if enough time has passed and checking is enabled."""
        if not self._check_enabled():
            return False
        state = self._load_state()
        last = state.get("checked_at", 0)
        return (time.time() - last) >= self._check_interval()

    # ── PyPI query ──

    def check_pypi(self, timeout: float = 10.0) -> Dict[str, Any]:
        """Query PyPI for the latest beacon-skill version.

        Returns dict with current, latest, update_available, checked_at.
        Saves result to state file.
        """
        current = __version__
        now = int(time.time())
        result: Dict[str, Any] = {
            "current": current,
            "latest": current,
            "update_available": False,
            "checked_at": now,
        }

        try:
            resp = requests.get(PYPI_URL, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            latest = data.get("info", {}).get("version", current)
            result["latest"] = latest
            result["update_available"] = _is_newer(latest, current)
        except Exception as exc:
            result["error"] = str(exc)

        # Persist
        state = self._load_state()
        state.update(result)
        self._save_state(state)

        return result

    # ── Cached status (no network) ──

    def cached_status(self) -> Dict[str, Any]:
        """Return the last known update state without hitting the network."""
        state = self._load_state()
        if not state:
            return {
                "current": __version__,
                "latest": __version__,
                "update_available": False,
                "checked_at": 0,
                "note": "never_checked",
            }
        # Ensure current reflects the running version
        state["current"] = __version__
        state["update_available"] = _is_newer(
            state.get("latest", __version__), __version__,
        )
        return state

    # ── Upgrade ──

    def do_upgrade(self, dry_run: bool = False) -> Dict[str, Any]:
        """Upgrade beacon-skill via pip.

        Args:
            dry_run: If True, return the command without executing.

        Returns:
            Dict with ok, command, output/error fields.
        """
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "beacon-skill"]
        result: Dict[str, Any] = {"command": " ".join(cmd)}

        if dry_run:
            result["dry_run"] = True
            result["ok"] = True
            return result

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            result["ok"] = proc.returncode == 0
            result["output"] = proc.stdout.strip()
            if proc.returncode != 0:
                result["error"] = proc.stderr.strip()
        except Exception as exc:
            result["ok"] = False
            result["error"] = str(exc)

        return result

    # ── Dismiss ──

    def dismiss(self, version: str) -> None:
        """Silence update notification for a specific version."""
        state = self._load_state()
        dismissed = state.get("dismissed", [])
        if version not in dismissed:
            dismissed.append(version)
        state["dismissed"] = dismissed
        self._save_state(state)

    def is_dismissed(self, version: str) -> bool:
        """Check if notifications for *version* have been silenced."""
        state = self._load_state()
        return version in state.get("dismissed", [])
