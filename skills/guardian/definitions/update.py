#!/usr/bin/env python3
"""Definition update utility for Guardian signature feeds."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

DEFAULT_UPDATE_URL = "https://raw.githubusercontent.com/guardian-defs/main/manifest.json"


def skill_root() -> Path:
    """Return Guardian skill root directory."""
    return Path(__file__).resolve().parents[1]


def resolve_workspace() -> Path:
    """Resolve workspace path based on env fallback chain."""
    guardian_workspace = os.environ.get("GUARDIAN_WORKSPACE")
    if guardian_workspace:
        return Path(guardian_workspace).expanduser().resolve()
    openclaw_workspace = os.environ.get("OPENCLAW_WORKSPACE")
    if openclaw_workspace:
        return Path(openclaw_workspace).expanduser().resolve()
    default_workspace = Path.home() / ".openclaw" / "workspace"
    if default_workspace.exists():
        return default_workspace.resolve()
    return Path.cwd().resolve()


def load_config() -> Dict[str, Any]:
    """Load Guardian config, preferring OpenClaw Control UI config when available."""
    sys.path.insert(0, str(skill_root() / "core"))
    from settings import load_config as shared_load_config  # type: ignore  # noqa: E402

    return shared_load_config()


def resolve_db_path(config: Dict[str, Any]) -> Path:
    """Resolve db path from config or default workspace location."""
    raw = config.get("db_path", "auto")
    if not raw or raw == "auto":
        return resolve_workspace() / "guardian.db"
    return Path(str(raw)).expanduser().resolve()


def definitions_dir() -> Path:
    """Return local definitions folder."""
    return skill_root() / "definitions"


def load_local_manifest() -> Dict[str, Any]:
    """Load local definition manifest payload."""
    manifest_path = definitions_dir() / "manifest.json"
    if not manifest_path.exists():
        return {"version": "0.0.0", "files": {}}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def update_url(config: Dict[str, Any]) -> str:
    """Resolve definitions update URL from config with default."""
    defs_cfg = config.get("definitions", {}) if isinstance(config.get("definitions"), dict) else {}
    configured = defs_cfg.get("update_url")
    return str(configured) if configured else DEFAULT_UPDATE_URL


def fetch_json(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    """Fetch JSON object from URL."""
    req = Request(url, headers={"User-Agent": "guardian-update/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8")
    payload = json.loads(data)
    if not isinstance(payload, dict):
        raise ValueError("Remote payload is not a JSON object")
    return payload


def version_tuple(version: str) -> Tuple[int, ...]:
    """Convert semantic-ish version text to comparable tuple."""
    parts = re.findall(r"\d+", version)
    return tuple(int(part) for part in parts) if parts else (0,)


def is_newer_version(current: str, available: str) -> bool:
    """Return True when available version is newer than current."""
    return version_tuple(available) > version_tuple(current)


def _candidate_urls(base_url: str, file_name: str, file_meta: Any) -> List[str]:
    """Build URL candidates for a definition file from manifest metadata."""
    candidates: List[str] = []
    if isinstance(file_meta, str):
        candidates.append(file_meta)
    elif isinstance(file_meta, dict):
        if isinstance(file_meta.get("url"), str):
            candidates.append(file_meta["url"])
        if isinstance(file_meta.get("path"), str):
            candidates.append(file_meta["path"])

    candidates.append(file_name)
    resolved = []
    for candidate in candidates:
        resolved.append(urljoin(base_url, candidate))
    return resolved


def _fetch_text(url: str, timeout: float = 10.0) -> str:
    req = Request(url, headers={"User-Agent": "guardian-update/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def fetch_definition_files(manifest: Dict[str, Any], manifest_url: str) -> Dict[str, str]:
    """Download all definition files listed in remote manifest."""
    files_meta = manifest.get("files", {})
    if not isinstance(files_meta, dict) or not files_meta:
        raise ValueError("Remote manifest has no files mapping")

    base = manifest_url.rsplit("/", 1)[0] + "/"
    downloaded: Dict[str, str] = {}
    for file_name, file_meta in files_meta.items():
        if not str(file_name).endswith(".json"):
            continue

        last_err: Optional[Exception] = None
        for url in _candidate_urls(base, str(file_name), file_meta):
            try:
                downloaded[str(file_name)] = _fetch_text(url)
                break
            except (URLError, OSError, ValueError) as exc:
                last_err = exc
        else:
            raise RuntimeError(f"Failed to download {file_name}: {last_err}")

    if "manifest.json" not in downloaded:
        downloaded["manifest.json"] = json.dumps(manifest, indent=2)
    return downloaded


def _extract_items(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    if "signatures" in payload and isinstance(payload["signatures"], list):
        return payload["signatures"]
    if "checks" in payload and isinstance(payload["checks"], list):
        return payload["checks"]
    return []


def validate_definition_files(files: Dict[str, str]) -> None:
    """Validate downloaded definitions by JSON parse and regex compile checks."""
    for name, body in files.items():
        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            raise ValueError(f"{name} is not a JSON object")
        if not name.endswith(".json"):
            continue
        if name == "manifest.json":
            continue
        for item in _extract_items(parsed):
            pattern = item.get("pattern")
            if isinstance(pattern, str) and pattern:
                re.compile(pattern)
            detection = item.get("detection")
            if isinstance(detection, dict):
                patterns = detection.get("patterns", [])
                if isinstance(patterns, list):
                    for candidate in patterns:
                        if isinstance(candidate, str) and candidate:
                            re.compile(candidate)


def backup_local_definitions(target_dir: Path) -> Path:
    """Backup current definitions directory before applying updates."""
    backups_root = target_dir / "backups"
    backups_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = backups_root / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    for path in target_dir.glob("*.json"):
        shutil.copy2(path, backup_dir / path.name)
    return backup_dir


def apply_definition_files(target_dir: Path, files: Dict[str, str]) -> None:
    """Apply validated files atomically using temp files and replace."""
    for name, body in files.items():
        destination = target_dir / name
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(target_dir)) as tmp:
            tmp.write(body)
            temp_path = Path(tmp.name)
        temp_path.replace(destination)


def ensure_update_table(conn: sqlite3.Connection) -> None:
    """Create update history table when missing."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS definition_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checked_at TEXT NOT NULL,
            from_version TEXT,
            to_version TEXT,
            update_url TEXT,
            applied INTEGER DEFAULT 0,
            status TEXT,
            note TEXT
        )
        """
    )
    conn.commit()


def record_update_event(
    db_path: Path,
    from_version: str,
    to_version: str,
    url: str,
    applied: bool,
    status: str,
    note: str,
) -> None:
    """Record update check/apply history in guardian.db."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        ensure_update_table(conn)
        conn.execute(
            """
            INSERT INTO definition_updates (checked_at, from_version, to_version, update_url, applied, status, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                from_version,
                to_version,
                url,
                1 if applied else 0,
                status,
                note,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def check_updates(apply: bool = False) -> Tuple[int, Dict[str, Any]]:
    """Check remote feed and optionally apply definition updates."""
    config = load_config()
    manifest_url = update_url(config)
    local_manifest = load_local_manifest()
    local_version = str(local_manifest.get("version", "0.0.0"))
    db_path = resolve_db_path(config)

    try:
        remote_manifest = fetch_json(manifest_url)
        remote_version = str(remote_manifest.get("version", "0.0.0"))
    except Exception as exc:  # noqa: BLE001
        record_update_event(db_path, local_version, local_version, manifest_url, False, "error", str(exc))
        return 1, {
            "ok": False,
            "current_version": local_version,
            "available_version": None,
            "update_url": manifest_url,
            "error": str(exc),
        }

    newer = is_newer_version(local_version, remote_version)
    payload: Dict[str, Any] = {
        "ok": True,
        "current_version": local_version,
        "available_version": remote_version,
        "update_url": manifest_url,
        "update_available": newer,
        "applied": False,
    }

    if not newer:
        record_update_event(db_path, local_version, remote_version, manifest_url, False, "current", "Already up-to-date")
        return 0, payload

    if not apply:
        record_update_event(db_path, local_version, remote_version, manifest_url, False, "available", "Update available")
        return 0, payload

    defs_target = definitions_dir()
    try:
        files = fetch_definition_files(remote_manifest, manifest_url)
        validate_definition_files(files)
        backup_dir = backup_local_definitions(defs_target)
        apply_definition_files(defs_target, files)
        payload["applied"] = True
        payload["backup_dir"] = str(backup_dir)
        record_update_event(db_path, local_version, remote_version, manifest_url, True, "applied", "Update applied")
        return 0, payload
    except Exception as exc:  # noqa: BLE001
        record_update_event(db_path, local_version, remote_version, manifest_url, False, "error", str(exc))
        return 1, {**payload, "ok": False, "error": str(exc)}


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for update utility."""
    parser = argparse.ArgumentParser(description="Guardian definition updater")
    parser.add_argument("--apply", action="store_true", help="Download and apply updates")
    parser.add_argument("--version", action="store_true", help="Show current and available versions")
    return parser


def main() -> int:
    """CLI entrypoint."""
    args = build_parser().parse_args()
    code, payload = check_updates(apply=args.apply)

    if args.version:
        print(
            json.dumps(
                {
                    "current_version": payload.get("current_version"),
                    "available_version": payload.get("available_version"),
                    "update_available": payload.get("update_available"),
                }
            )
        )
        return code

    print(json.dumps(payload))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
