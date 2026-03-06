#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

HOME = Path.home()
PROJECT_OS_HOME = HOME / ".project_os"
CONFIG_PATH = Path(os.environ.get("PROJECT_OS_CONFIG", str(PROJECT_OS_HOME / "openclaw_test_config.json")))
DB_PATH = Path(os.environ.get("PROJECT_OS_DB", str(PROJECT_OS_HOME / "openclaw_test.db")))
MEMORY_PATH = Path(os.environ.get("PROJECT_OS_MEMORY", str(PROJECT_OS_HOME / "PROJECT_MEMORY.md")))

CANDIDATE_ROOTS = [
    HOME / "GitHub",
    HOME / "GitHub-Organized",
    HOME / "claude-workspaces",
    HOME / "Claude Code",
    HOME / ".openclaw" / "workspace",
]

CANDIDATE_CONVERSATION_ROOTS = [
    HOME / ".claude",
    HOME / "Claude Code",
    HOME / ".codex",
    HOME / ".openclaw",
]


def bool_env(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "")
    if not raw.strip():
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def existing_dirs(paths: list[Path]) -> list[str]:
    out: list[str] = []
    for path in paths:
        if path.exists() and path.is_dir():
            out.append(str(path))
    return out


def auto_extra_roots() -> list[str]:
    extras: list[str] = []
    for child in HOME.iterdir():
        if not child.is_dir():
            continue
        lowered = child.name.lower()
        if any(token in lowered for token in ["workspace", "projects", "github", "repos"]):
            extras.append(str(child))
    return sorted(set(extras))


def env_extra_roots() -> list[str]:
    raw = os.environ.get("PROJECT_OS_EXTRA_ROOTS", "")
    if not raw.strip():
        return []
    extras: list[str] = []
    for segment in raw.split(":"):
        candidate = Path(segment.strip()).expanduser()
        if candidate.exists() and candidate.is_dir():
            extras.append(str(candidate))
    return sorted(set(extras))


def detect_github_username(enabled: bool) -> str:
    if not enabled:
        return ""

    env_name = os.environ.get("GITHUB_USERNAME", "").strip()
    if env_name:
        return env_name

    try:
        proc = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
        )
        if proc.returncode == 0:
            login = proc.stdout.strip()
            if login:
                return login
    except Exception:
        pass

    return ""


def main() -> int:
    PROJECT_OS_HOME.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)

    privacy_mode = os.environ.get("PROJECT_OS_PRIVACY_MODE", "strict").strip().lower() or "strict"
    enable_home_discovery = bool_env("PROJECT_OS_ENABLE_HOME_DISCOVERY", False)
    include_chat_roots = bool_env("PROJECT_OS_INCLUDE_CHAT_ROOTS", False)
    enable_github_sync = bool_env("PROJECT_OS_ENABLE_GITHUB_SYNC", False)

    local_roots = existing_dirs(CANDIDATE_ROOTS)
    if enable_home_discovery:
        local_roots.extend(auto_extra_roots())
    local_roots.extend(env_extra_roots())
    local_roots = sorted(set(local_roots))

    conversation_roots: list[str] = []
    if include_chat_roots:
        conversation_roots = sorted(set(existing_dirs(CANDIDATE_CONVERSATION_ROOTS)))

    github_username = detect_github_username(enable_github_sync)
    github_token_env_var = "GITHUB_TOKEN" if enable_github_sync else ""

    config = {
        "local_roots": local_roots,
        "include_non_git_projects": True,
        "include_nested_non_git_projects": False,
        "prune_missing_local_projects": True,
        "include_collection_projects": True,
        "collection_dir_names": ["codex_projects"],
        "ignore_project_path_patterns": [
            r"/\.openclaw/workspace/skills/",
            r"/\.codex/skills/",
            r"/clawd/skills/",
        ],
        "github": {"username": github_username, "token_env_var": github_token_env_var},
        "conversation_roots": conversation_roots,
        "session_index_max_files": 1500 if privacy_mode == "strict" else 3500,
        "create_chat_projects": bool(include_chat_roots),
        "auto_squash_chat_projects": True,
        "prune_missing_sessions": True,
        "memory_file_path": str(MEMORY_PATH),
        "privacy_mode": privacy_mode,
        "servers": [],
    }

    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")

    print(f"Wrote config: {CONFIG_PATH}")
    print(f"DB path: {DB_PATH}")
    print("Local roots:")
    for root in local_roots:
        print(f"- {root}")
    print("Conversation roots:")
    for root in conversation_roots:
        print(f"- {root}")
    if not conversation_roots:
        print("- (disabled by default; set PROJECT_OS_INCLUDE_CHAT_ROOTS=1 to enable)")
    github_name = config["github"]["username"] or "(disabled)"
    print(f"GitHub username: {github_name}")
    print(f"Privacy mode: {privacy_mode}")
    print(f"Home auto-discovery: {'enabled' if enable_home_discovery else 'disabled'}")
    print(f"Chat transcript indexing: {'enabled' if include_chat_roots else 'disabled'}")
    print(f"GitHub sync: {'enabled' if enable_github_sync else 'disabled'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
