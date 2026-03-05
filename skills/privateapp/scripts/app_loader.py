"""App plugin discovery and loading for Private App.

Architecture:
  - Built-in apps ship inside Private App (apps/ directory)
  - Local apps are placed in ~/.local/share/privateapp/apps/ by the user
  - User can add extra scan paths via Settings API


Scan (runs on startup + manual rescan):
  1. Load built-in apps from apps/
  2. Load apps from shared local folder + user-configured paths
  3. Registry fallback for uninstalled apps
"""
from __future__ import annotations

import importlib.util
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import NamedTuple

from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

log = logging.getLogger("privateapp.loader")

# Default shared apps directory
DEFAULT_APPS_DIR = Path("~/.local/share/privateapp/apps").expanduser()


class AppInfo(NamedTuple):
    id: str
    name: str
    icon: str
    version: str
    description: str
    author: str
    builtin: bool
    shortcode: str
    api_prefix: str
    url: str
    has_routes: bool = False
    has_frontend: bool = False
    external: bool = False
    detected: bool = False
    installed: bool = False
    source: str = ""  # "builtin", "local", "registry"


# ── Settings DB ──────────────────────────────────────────────────────

_SETTINGS_DB: Path | None = None


def init_settings_db(data_dir: Path) -> None:
    """Initialize the settings DB. Call once at startup."""
    global _SETTINGS_DB
    _SETTINGS_DB = data_dir / "privateapp.db"
    conn = sqlite3.connect(str(_SETTINGS_DB))
    conn.execute("""CREATE TABLE IF NOT EXISTS app_state (
        app_id TEXT PRIMARY KEY,
        enabled INTEGER NOT NULL DEFAULT 1,
        updated_at TEXT DEFAULT (datetime('now'))
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS discovery_paths (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL UNIQUE,
        label TEXT NOT NULL DEFAULT '',
        enabled INTEGER NOT NULL DEFAULT 1,
        added_at TEXT DEFAULT (datetime('now'))
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS preferences (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    conn.commit()
    conn.close()

    # Ensure default local apps dir exists
    DEFAULT_APPS_DIR.mkdir(parents=True, exist_ok=True)


def _settings_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_SETTINGS_DB))
    conn.row_factory = sqlite3.Row
    return conn


# ── App state (enable/disable) ───────────────────────────────────────

def is_app_enabled(app_id: str, default: bool = True) -> bool:
    conn = _settings_conn()
    row = conn.execute("SELECT enabled FROM app_state WHERE app_id=?", (app_id,)).fetchone()
    conn.close()
    return bool(row["enabled"]) if row else default


def set_app_enabled(app_id: str, enabled: bool) -> None:
    conn = _settings_conn()
    conn.execute(
        """INSERT INTO app_state (app_id, enabled) VALUES (?, ?)
           ON CONFLICT(app_id) DO UPDATE SET enabled=excluded.enabled, updated_at=datetime('now')""",
        (app_id, 1 if enabled else 0),
    )
    conn.commit()
    conn.close()


# ── Discovery paths ──────────────────────────────────────────────────

def get_discovery_paths() -> list[dict]:
    """Return all user-configured discovery paths."""
    conn = _settings_conn()
    rows = conn.execute(
        "SELECT id, path, label, enabled FROM discovery_paths ORDER BY id"
    ).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "path": r["path"],
            "label": r["label"],
            "enabled": bool(r["enabled"]),
            "exists": Path(r["path"]).is_dir(),
        }
        for r in rows
    ]


def add_discovery_path(path: str, label: str = "") -> dict:
    """Add a new discovery path (scanned for app.json directories)."""
    expanded = str(Path(path).expanduser().resolve())
    conn = _settings_conn()
    try:
        conn.execute(
            "INSERT INTO discovery_paths (path, label) VALUES (?, ?)",
            (expanded, label or Path(expanded).name),
        )
        conn.commit()
        row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Path already registered: {expanded}")
    conn.close()
    Path(expanded).mkdir(parents=True, exist_ok=True)
    return {"id": row_id, "path": expanded, "label": label or Path(expanded).name, "enabled": True}


def remove_discovery_path(path_id: int) -> bool:
    conn = _settings_conn()
    cursor = conn.execute("DELETE FROM discovery_paths WHERE id=?", (path_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def toggle_discovery_path(path_id: int, enabled: bool) -> bool:
    conn = _settings_conn()
    cursor = conn.execute(
        "UPDATE discovery_paths SET enabled=? WHERE id=?", (1 if enabled else 0, path_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


# ── Preferences ──────────────────────────────────────────────────────

def get_preference(key: str, default: str = "") -> str:
    conn = _settings_conn()
    row = conn.execute("SELECT value FROM preferences WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_preference(key: str, value: str) -> None:
    conn = _settings_conn()
    conn.execute(
        "INSERT INTO preferences (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()
    conn.close()


# ── Detection helpers ────────────────────────────────────────────────

def _check_detect(detect: dict) -> bool:
    """Check if an app's required data exists on disk."""
    if not detect:
        return True
    for key in ("db_path", "file_path"):
        val = detect.get(key)
        if val and not Path(val).expanduser().exists():
            return False
    return True


# ── Router loading ───────────────────────────────────────────────────

def _load_router(routes_py: Path, module_name: str) -> APIRouter | None:
    if not routes_py.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location(module_name, str(routes_py))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        if hasattr(module, "router"):
            return module.router
        log.warning(f"'{module_name}' routes.py has no 'router'")
    except Exception as e:
        log.error(f"Failed to load routes for '{module_name}': {e}")
    return None


# ── Single app loading ───────────────────────────────────────────────

def _load_app_from_dir(
    app_dir: Path,
    source: str,
    fastapi_app=None,
) -> tuple[AppInfo | None, tuple[str, APIRouter] | None]:
    """Load a single app from a directory containing app.json."""
    app_json_path = app_dir / "app.json"
    if not app_json_path.exists():
        return None, None

    try:
        meta = json.loads(app_json_path.read_text())
    except Exception as e:
        log.warning(f"Failed to parse {app_json_path}: {e}")
        return None, None

    app_id = meta.get("id", app_dir.name)
    shortcode = meta.get("shortcode", app_id)
    api_prefix = f"/api/app/{shortcode}"
    app_url = f"/app/{app_id}/"
    is_builtin = (source == "builtin")

    detect = meta.get("detect", {})
    detected = _check_detect(detect) if not is_builtin else True

    # Backend routes
    routes_py = app_dir / "backend" / "routes.py"
    has_routes = False
    router_pair = None
    module_name = f"privateapp_{app_id.replace('-', '_')}"

    if detected:
        router = _load_router(routes_py, module_name)
        if router is not None:
            router_pair = (api_prefix, router)
            has_routes = True

    # Frontend
    has_frontend = False
    frontend_dist = app_dir / "frontend" / "dist"
    if frontend_dist.is_dir() and detected:
        if fastapi_app is not None:
            try:
                fastapi_app.mount(
                    f"/app/{app_id}",
                    StaticFiles(directory=str(frontend_dist), html=True),
                    name=f"app-{app_id}",
                )
                has_frontend = True
            except Exception as e:
                log.warning(f"Could not mount frontend for '{app_id}': {e}")
        else:
            has_frontend = True

    info = AppInfo(
        id=app_id,
        name=meta.get("name", app_id),
        icon=meta.get("icon", "📦"),
        version=meta.get("version", "1.0.0"),
        description=meta.get("description", ""),
        author=meta.get("author", ""),
        builtin=is_builtin,
        shortcode=shortcode,
        api_prefix=api_prefix,
        url=app_url,
        has_routes=has_routes,
        has_frontend=has_frontend,
        external=not is_builtin,
        detected=detected,
        installed=detected,
        source=source,
    )

    log.info(f"App '{app_id}' [{shortcode}] — {source}, {'active' if detected else 'not detected'}")
    return info, router_pair


# ── Discovery ────────────────────────────────────────────────────────

def discover_app_dirs(
    builtin_apps_dir: Path,
) -> list[tuple[Path, dict, str]]:
    """Discover all app directories.

    Returns list of (app_dir, meta, source) tuples.
    """
    results: list[tuple[Path, dict, str]] = []
    seen_ids: set[str] = set()

    # 1. Built-in apps
    if builtin_apps_dir.is_dir():
        for app_dir in sorted(builtin_apps_dir.iterdir()):
            if not app_dir.is_dir():
                continue
            app_json = app_dir / "app.json"
            if not app_json.exists():
                continue
            try:
                meta = json.loads(app_json.read_text())
                app_id = meta.get("id", app_dir.name)
                if app_id not in seen_ids:
                    results.append((app_dir, meta, "builtin"))
                    seen_ids.add(app_id)
            except Exception:
                continue

    # 2. Local apps: shared folder + user-configured paths
    scan_dirs: list[Path] = [DEFAULT_APPS_DIR]

    if _SETTINGS_DB and _SETTINGS_DB.exists():
        for dp in get_discovery_paths():
            if dp["enabled"] and dp["exists"]:
                p = Path(dp["path"])
                if p not in scan_dirs:
                    scan_dirs.append(p)

    for scan_dir in scan_dirs:
        if not scan_dir.is_dir():
            continue
        for app_dir in sorted(scan_dir.iterdir()):
            if not app_dir.is_dir():
                continue
            # Resolve symlinks
            real_dir = app_dir.resolve() if app_dir.is_symlink() else app_dir
            app_json = real_dir / "app.json"
            if not app_json.exists():
                continue
            try:
                meta = json.loads(app_json.read_text())
                app_id = meta.get("id", app_dir.name)
                if app_id not in seen_ids:
                    results.append((real_dir, meta, "local"))
                    seen_ids.add(app_id)
            except Exception:
                continue

    return results


# ── Main load ────────────────────────────────────────────────────────

def load_apps(
    builtin_apps_dir: Path,
    registry_dir: Path,
    fastapi_app=None,
) -> tuple[list[AppInfo], list[tuple[str, APIRouter]]]:
    """Load all apps: built-in + local + registry."""
    apps: list[AppInfo] = []
    routers: list[tuple[str, APIRouter]] = []
    seen_ids: set[str] = set()

    for app_dir, meta, source in discover_app_dirs(builtin_apps_dir):
        app_id = meta.get("id", app_dir.name)
        if app_id in seen_ids:
            continue

        info, router_pair = _load_app_from_dir(
            app_dir, source=source, fastapi_app=fastapi_app,
        )
        if info:
            apps.append(info)
            seen_ids.add(info.id)
            if router_pair:
                routers.append(router_pair)

    # Registry fallback
    if registry_dir.is_dir():
        for reg_file in sorted(registry_dir.glob("*.json")):
            try:
                meta = json.loads(reg_file.read_text())
                app_id = meta.get("id", reg_file.stem)
            except Exception:
                continue
            if app_id in seen_ids:
                continue

            shortcode = meta.get("shortcode", app_id)
            detected = _check_detect(meta.get("detect", {}))

            apps.append(AppInfo(
                id=app_id,
                name=meta.get("name", app_id),
                icon=meta.get("icon", "📦"),
                version=meta.get("version", "1.0.0"),
                description=meta.get("description", ""),
                author=meta.get("author", ""),
                builtin=False,
                shortcode=shortcode,
                api_prefix=f"/api/app/{shortcode}",
                url=f"/app/{app_id}/",
                external=True,
                detected=detected,
                installed=detected,
                source="registry",
            ))

    return apps, routers
