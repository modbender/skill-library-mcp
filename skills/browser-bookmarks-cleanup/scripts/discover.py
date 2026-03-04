"""Discover browser profiles (Chrome and Firefox) on macOS."""

from __future__ import annotations

import argparse
import configparser
import json
import sys
from pathlib import Path
from typing import Any

from _common import BROWSER_ROOTS, normalize_name, now_iso


def _chrome_local_state_info(chrome_root: Path) -> dict[str, dict[str, Any]]:
    local_state = chrome_root / "Local State"
    if not local_state.exists():
        return {}
    try:
        payload = json.loads(local_state.read_text(encoding="utf-8"))
    except Exception:
        return {}
    info_cache = payload.get("profile", {}).get("info_cache", {})
    return {k: v for k, v in info_cache.items() if isinstance(v, dict)}


def list_chrome_profiles(chrome_root: Path) -> list[dict[str, Any]]:
    if not chrome_root.exists():
        return []
    info_cache = _chrome_local_state_info(chrome_root)
    profiles = []
    for child in sorted(chrome_root.iterdir()):
        if not child.is_dir():
            continue
        bookmarks = child / "Bookmarks"
        if not bookmarks.exists():
            continue
        history = child / "History"
        meta = info_cache.get(child.name, {})
        profile_name = normalize_name(meta.get("name", "")) or child.name
        account_name = normalize_name(meta.get("gaia_name", "")) or None
        display = f"{profile_name} ({account_name})" if account_name and account_name.lower() != profile_name.lower() else profile_name
        profiles.append({
            "browser": "chrome",
            "profile_dir": child.name,
            "profile_name": profile_name,
            "display_name": display,
            "account_name": account_name,
            "account_email": normalize_name(meta.get("user_name", "")) or None,
            "bookmarks_path": str(bookmarks),
            "history_path": str(history) if history.exists() else None,
        })
    return profiles


def list_firefox_profiles(firefox_root: Path) -> list[dict[str, Any]]:
    if not firefox_root.exists():
        return []
    ini_path = firefox_root / "profiles.ini"
    if not ini_path.exists():
        return []
    config = configparser.ConfigParser()
    config.read(str(ini_path))
    profiles = []
    for section in config.sections():
        if not section.startswith("Profile"):
            continue
        name = config.get(section, "Name", fallback=None)
        path_val = config.get(section, "Path", fallback=None)
        is_relative = config.get(section, "IsRelative", fallback="1") == "1"
        if not path_val:
            continue
        profile_dir = firefox_root / path_val if is_relative else Path(path_val)
        places = profile_dir / "places.sqlite"
        if not places.exists():
            continue
        profiles.append({
            "browser": "firefox",
            "profile_dir": str(profile_dir),
            "profile_name": name or profile_dir.name,
            "display_name": name or profile_dir.name,
            "bookmarks_path": str(places),
            "history_path": str(places),
        })
    return profiles


def run(args: argparse.Namespace) -> int:
    browser = args.browser
    profiles: list[dict[str, Any]] = []
    if browser in ("chrome", "all"):
        profiles += list_chrome_profiles(Path(BROWSER_ROOTS["chrome"]).expanduser())
    if browser in ("firefox", "all"):
        profiles += list_firefox_profiles(Path(BROWSER_ROOTS["firefox"]).expanduser())
    sys.stdout.write(json.dumps({"generated_at": now_iso(), "profiles": profiles}, indent=2, ensure_ascii=False) + "\n")
    return 0


def add_subparser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("discover", help="List browser profiles.")
    p.add_argument("--browser", choices=["chrome", "firefox", "all"], default="all")
    p.set_defaults(func=run)
