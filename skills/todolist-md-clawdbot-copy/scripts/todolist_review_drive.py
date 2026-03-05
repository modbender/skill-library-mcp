#!/usr/bin/env python3
"""todolist_review_drive.py

Code-first change detection for todolist-md Markdown files in Google Drive.

Goal:
- Avoid LLM/token usage unless a file actually changed since last review.
- Maintain a local state file keyed by Drive fileId.

This script intentionally does NOT call an LLM.
It only:
1) Lists files in a Drive folder (rootFolderId)
2) Compares modifiedTime/size to stored state
3) Optionally downloads changed files and updates a top-of-file last_review header

Notes:
- `gog drive search` is full-text search; for folder listing use `gog drive ls --parent <folderId> --json`. (gog v0.9.0+)
- Requires `gog` already authenticated for Drive.

Example:
  ./scripts/todolist_review_drive.py \
    --root-folder-id 1bqC8mceie8KsqjVMKEcJUPPBRopU9uwu \
    --state ./outputs/todolist_review_state.json \
    --write-last-review
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List


def iso_utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sh(cmd: List[str], env: Dict[str, str] | None = None) -> str:
    out = subprocess.check_output(cmd, env=env, text=True)
    return out


def gog_env() -> Dict[str, str]:
    # Use same pattern as TOOLS.md: run as ubuntu and pass GOG_ACCOUNT/GOG_KEYRING_PASSWORD.
    # Here we just forward current environment; caller should export vars.
    env = os.environ.copy()
    if not env.get("GOG_BIN"):
        env["GOG_BIN"] = "/home/linuxbrew/.linuxbrew/bin/gog"
    return env


def gog_drive_ls(folder_id: str) -> List[Dict[str, Any]]:
    env = gog_env()
    gog = env["GOG_BIN"]
    cmd = [
        "sudo",
        "-u",
        "ubuntu",
        "-H",
        "env",
        f"GOG_ACCOUNT={env.get('GOG_ACCOUNT','')}",
        f"GOG_KEYRING_PASSWORD={env.get('GOG_KEYRING_PASSWORD','')}",
        gog,
        "drive",
        "ls",
        "--parent",
        folder_id,
        "--json",
    ]
    raw = sh(cmd)
    data = json.loads(raw)
    # gog v0.9.0 shape: {"files":[...]} or {"items":[...]}
    return data.get("files") or data.get("items") or []


def gog_drive_download(file_id: str, out_path: Path) -> None:
    env = gog_env()
    gog = env["GOG_BIN"]
    cmd = [
        "sudo",
        "-u",
        "ubuntu",
        "-H",
        "env",
        f"GOG_ACCOUNT={env.get('GOG_ACCOUNT','')}",
        f"GOG_KEYRING_PASSWORD={env.get('GOG_KEYRING_PASSWORD','')}",
        gog,
        "drive",
        "download",
        file_id,
        "--out",
        str(out_path),
    ]
    sh(cmd)


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def ensure_last_review_header(text: str, stamp: str, root_folder_id: str, model: str) -> str:
    """Option B behavior:
    - If header exists in first ~5 lines: update it in-place.
    - If header does not exist: insert at very top.

    Caller should only choose insertion when user opted into Option B.
    """
    header_prefix = "<!-- bot: last_review -->"
    header_line = f"{header_prefix} {stamp} root={root_folder_id} model={model}"

    lines = text.splitlines()
    scan = min(5, len(lines))
    for i in range(scan):
        if lines[i].startswith(header_prefix):
            lines[i] = header_line
            return "\n".join(lines) + ("\n" if text.endswith("\n") else "")

    # Insert at top
    return header_line + "\n" + text


def load_state(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"files": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root-folder-id", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--model", default="gpt-4o")
    ap.add_argument("--write-last-review", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    state_path = Path(args.state)
    state = load_state(state_path)
    files_state = state.setdefault("files", {})

    files = gog_drive_ls(args.root_folder_id)
    # only markdown-ish
    md_files = [f for f in files if (f.get("name", "").endswith(".md") or f.get("mimeType") == "text/markdown")]

    changed: List[Dict[str, Any]] = []
    for f in md_files:
        fid = f.get("id")
        if not fid:
            continue
        mtime = f.get("modifiedTime")
        size = f.get("size")
        prev = files_state.get(fid, {})
        if prev.get("modifiedTime") != mtime or prev.get("size") != size:
            changed.append(f)

    print(json.dumps({
        "rootFolderId": args.root_folder_id,
        "totalMarkdown": len(md_files),
        "changed": [{"id": f.get("id"), "name": f.get("name"), "modifiedTime": f.get("modifiedTime"), "size": f.get("size")} for f in changed]
    }, indent=2))

    # Update state for unchanged too (so new files are tracked)
    for f in md_files:
        fid = f.get("id")
        files_state.setdefault(fid, {})
        files_state[fid]["modifiedTime"] = f.get("modifiedTime")
        files_state[fid]["size"] = f.get("size")

    # Optionally stamp header on changed files
    if args.write_last_review and changed:
        stamp = iso_utc_now()
        for f in changed:
            fid = f["id"]
            tmp = Path(f"/tmp/{fid}.md")
            gog_drive_download(fid, tmp)
            old = tmp.read_text(encoding="utf-8")
            new = ensure_last_review_header(old, stamp, args.root_folder_id, args.model)
            if sha256_text(old) == sha256_text(new):
                continue
            if args.dry_run:
                print(f"[dry-run] would update last_review header for {f.get('name')} ({fid})")
            else:
                # NOTE: actual upload/in-place update should be implemented by the agent using Drive API files.update.
                # We intentionally do not embed secrets/token logic here.
                tmp.write_text(new, encoding="utf-8")
                print(f"[needs-agent-upload] updated local copy for {f.get('name')} ({fid})")

    state["lastScanAtUtc"] = iso_utc_now()
    save_state(state_path, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
