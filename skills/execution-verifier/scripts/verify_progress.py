#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path


def file_info(path: Path):
    if not path.exists():
        return {"path": str(path), "exists": False}
    st = path.stat()
    return {
        "path": str(path),
        "exists": True,
        "mtime": int(st.st_mtime),
        "age_min": round((time.time() - st.st_mtime) / 60, 2),
        "size": st.st_size,
    }


def extract_backtick_paths(text: str):
    cands = re.findall(r"`([^`]+)`", text)
    out = []
    for c in cands:
        if "/" in c and not c.startswith("http"):
            out.append(c)
    return sorted(set(out))


def last_commit_age_min(repo_dir: Path):
    try:
        ts = subprocess.check_output(
            ["git", "-C", str(repo_dir), "log", "-1", "--format=%ct"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if not ts:
            return None
        return round((time.time() - int(ts)) / 60, 2)
    except Exception:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project-dir", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--open-tasks", required=True)
    p.add_argument("--window-min", type=int, default=30)
    args = p.parse_args()

    project_dir = Path(args.project_dir)
    status = Path(args.status)
    open_tasks = Path(args.open_tasks)

    checks = [file_info(status), file_info(open_tasks)]

    open_tasks_text = open_tasks.read_text(encoding="utf-8") if open_tasks.exists() else ""
    target_paths = extract_backtick_paths(open_tasks_text)

    for rel in target_paths[:8]:
        pth = Path(rel)
        if not pth.is_absolute():
            pth = Path.cwd() / rel
        checks.append(file_info(pth))

    recent_file_changes = [
        c for c in checks if c.get("exists") and c.get("age_min", 999999) <= args.window_min
    ]

    commit_age = last_commit_age_min(project_dir)
    recent_commit = commit_age is not None and commit_age <= args.window_min

    progress = bool(recent_file_changes or recent_commit)

    blockers = []
    if not progress:
        blockers.append(f"No file updates or commit within {args.window_min} minutes")

    result = {
        "ok": True,
        "window_min": args.window_min,
        "progress_detected": progress,
        "recent_file_changes": [c["path"] for c in recent_file_changes],
        "last_commit_age_min": commit_age,
        "blockers": blockers,
        "checked": checks,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
