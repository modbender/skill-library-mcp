#!/usr/bin/env python3
"""
tg-reader-check — offline diagnostic for tg-channel-reader skill.
Checks credentials, session files, and backend availability.
Outputs JSON; exits 0 if healthy, 1 if problems found.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# ── Session discovery ────────────────────────────────────────────────────────
# Copied from reader.py — we cannot import reader because it pulls in pyrogram
# at module level, and the whole point of this script is to work even when
# backends are not installed.

def _find_session_files() -> list:
    """Find .session files in home directory and current working directory."""
    found = []
    seen: set = set()
    dirs_checked: set = set()
    for d in [Path.home(), Path.cwd()]:
        d = d.resolve()
        if d in dirs_checked:
            continue
        dirs_checked.add(d)
        for pattern in ["*.session", ".*.session"]:
            for f in d.glob(pattern):
                if f.name.endswith("-journal"):
                    continue
                resolved = f.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                found.append(f)
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found


# ── Credential check ────────────────────────────────────────────────────────

def _check_credentials(config_file=None, session_file=None) -> tuple:
    """Check credential availability without exiting.

    Returns:
        (credentials_dict, resolved_session_name, default_session_name, problems_list)
    """
    problems: list = []

    api_id = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    default_session = str(Path.home() / ".tg-reader-session")
    session_name = os.environ.get("TG_SESSION", default_session)

    result: dict = {
        "source": None,
        "api_id_set": False,
        "api_hash_set": False,
    }

    # Env vars present?
    env_has_id = bool(api_id)
    env_has_hash = bool(api_hash)
    if env_has_id and env_has_hash:
        result["source"] = "env"

    # Config file state
    config_path = Path(config_file) if config_file else Path.home() / ".tg-reader.json"
    result["config_file"] = str(config_path)
    result["config_file_exists"] = config_path.exists()

    cfg_has_id = False
    cfg_has_hash = False
    cfg_session = None

    if config_path.exists():
        try:
            with open(config_path) as f:
                cfg = json.load(f)
            cfg_has_id = bool(cfg.get("api_id"))
            cfg_has_hash = bool(cfg.get("api_hash"))
            cfg_session = cfg.get("session")
            # Fallback to config values if env not set
            if not api_id and cfg_has_id:
                api_id = cfg.get("api_id")
            if not api_hash and cfg_has_hash:
                api_hash = cfg.get("api_hash")
            if cfg_session:
                session_name = cfg_session
        except (json.JSONDecodeError, OSError) as e:
            problems.append(f"Config file {config_path} is invalid: {e}")

    result["config_has_api_id"] = cfg_has_id
    result["config_has_api_hash"] = cfg_has_hash

    # Track config session override — a frequent source of mismatch
    if cfg_session:
        result["config_session_override"] = cfg_session

    # Determine source if not env
    if result["source"] is None and api_id and api_hash:
        result["source"] = "config_file"

    result["api_id_set"] = bool(api_id)
    result["api_hash_set"] = bool(api_hash)

    if not api_id:
        problems.append("TG_API_ID not found in env vars or config file")
    if not api_hash:
        problems.append("TG_API_HASH not found in env vars or config file")

    # Explicit --session-file overrides everything
    if session_file:
        session_name = session_file

    # Normalize: strip .session suffix if user passed full filename
    if session_name.endswith(".session"):
        session_name = session_name[: -len(".session")]
    if default_session.endswith(".session"):
        default_session = default_session[: -len(".session")]

    return result, session_name, default_session, problems


# ── Session check ────────────────────────────────────────────────────────────

def _check_session(session_name: str, default_session_name: str) -> tuple:
    """Check session file state.

    Args:
        session_name: resolved session name (after config/env/cli overrides)
        default_session_name: what the session name would be without overrides

    Returns:
        (session_dict, problems_list)
    """
    problems: list = []
    expected_path = Path(f"{session_name}.session")
    default_path = Path(f"{default_session_name}.session")

    result: dict = {
        "expected_path": str(expected_path),
        "exists": expected_path.exists(),
    }

    # Show default path when config overrides it — helps spot mismatch
    if str(expected_path) != str(default_path):
        result["default_path"] = str(default_path)
        result["default_exists"] = default_path.exists()

    expected_mtime = None
    if expected_path.exists():
        try:
            stat = expected_path.stat()
            expected_mtime = stat.st_mtime
            result["size"] = stat.st_size
            result["modified"] = datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).isoformat()
            if stat.st_size == 0:
                problems.append(
                    f"Session file exists but is empty (0 bytes): {expected_path}"
                )
        except OSError as e:
            problems.append(f"Cannot read session file {expected_path}: {e}")

    # Discover all session files
    found = _find_session_files()
    result["found_sessions"] = []
    newest_other = None
    newest_other_path = None
    for f in found:
        entry: dict = {"path": str(f)}
        try:
            fstat = f.stat()
            entry["size"] = fstat.st_size
            entry["modified"] = datetime.fromtimestamp(
                fstat.st_mtime, tz=timezone.utc
            ).isoformat()
            # Track the newest session that is NOT the expected one
            if f.resolve() != expected_path.resolve():
                if newest_other is None or fstat.st_mtime > newest_other:
                    newest_other = fstat.st_mtime
                    newest_other_path = f
        except OSError:
            entry["size"] = None
            entry["modified"] = None
        result["found_sessions"].append(entry)

    if not expected_path.exists():
        msg = f"Expected session file not found: {expected_path}"
        if found:
            suggestion = str(found[0]).removesuffix(".session")
            result["suggestion"] = f"--session-file {suggestion}"
            msg += f". Use --session-file {suggestion}"
        problems.append(msg)

    # Freshness warning: config points to an older session while a newer one exists
    elif expected_mtime and newest_other and newest_other > expected_mtime:
        newer = str(newest_other_path).removesuffix(".session")
        problems.append(
            f"Expected session ({expected_path}) is older than {newest_other_path}. "
            f"You may be using a stale session. "
            f"Consider: --session-file {newer} or update 'session' in ~/.tg-reader.json"
        )
        result["stale_warning"] = True
        result["newer_session"] = str(newest_other_path)

    return result, problems


# ── Backend check ────────────────────────────────────────────────────────────

def _check_backends() -> tuple:
    """Check importability and version of each backend library.

    Returns:
        (backends_dict, problems_list)
    """
    problems: list = []
    result: dict = {}

    for name in ("pyrogram", "telethon", "tgcrypto"):
        try:
            mod = __import__(name)
            version = getattr(mod, "__version__", "unknown")
            result[name] = {"installed": True, "version": version}
        except ImportError:
            result[name] = {"installed": False, "version": None}

    if not result["pyrogram"]["installed"] and not result["telethon"]["installed"]:
        problems.append(
            "No MTProto backend available. "
            "Install pyrogram or telethon: pip install pyrogram tgcrypto"
        )

    return result, problems


# ── Orchestration ────────────────────────────────────────────────────────────

def run_check(config_file=None, session_file=None) -> dict:
    """Run all diagnostic checks and return combined result."""
    all_problems: list = []

    credentials, session_name, default_session, cred_problems = _check_credentials(
        config_file, session_file
    )
    all_problems.extend(cred_problems)

    session, sess_problems = _check_session(session_name, default_session)
    all_problems.extend(sess_problems)

    backends, backend_problems = _check_backends()
    all_problems.extend(backend_problems)

    status = "ok" if not all_problems else "error"

    return {
        "status": status,
        "credentials": credentials,
        "session": session,
        "backends": backends,
        "problems": all_problems,
    }


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="tg-reader-check",
        description="Offline diagnostic check for tg-channel-reader skill",
    )
    parser.add_argument(
        "--config-file",
        default=None,
        help="Path to config JSON (overrides ~/.tg-reader.json)",
    )
    parser.add_argument(
        "--session-file",
        default=None,
        help="Path to session file (overrides default session path)",
    )

    args = parser.parse_args()
    result = run_check(args.config_file, args.session_file)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "ok" else 1)


if __name__ == "__main__":
    main()
