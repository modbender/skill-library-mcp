#!/usr/bin/env python3
"""Context Clean Up - Audit

A lightweight audit tool to locate the most likely sources of prompt bloat:
- large tool outputs persisted into session JSONL transcripts
- repeated cron/system messages
- oversized workspace bootstrap files (AGENTS.md, MEMORY.md, etc.)

Design goals:
- dependency-free (stdlib only)
- short stdout; optionally write detailed JSON to a file

Usage:
  python3 scripts/context_cleanup_audit.py --out memory/context-cleanup-audit.json
  python3 scripts/context_cleanup_audit.py --session ~/.openclaw/agents/main/sessions/<id>.jsonl

Exit code:
  0 on success
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


BOOTSTRAP_FILES = [
    "AGENTS.md",
    "SOUL.md",
    "TOOLS.md",
    "IDENTITY.md",
    "USER.md",
    "HEARTBEAT.md",
    "BOOTSTRAP.md",
    "MEMORY.md",
]


@dataclass
class TopItem:
    chars: int
    kind: str
    message_id: str
    role: str
    tool_name: str
    preview: str


def _preview(s: str, n: int = 220) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    return s[: n - 3] + "..."


def find_state_dir() -> Path:
    # Prefer explicit env, otherwise default to ~/.openclaw
    env = os.environ.get("OPENCLAW_STATE_DIR")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / ".openclaw").resolve()


def find_sessions_dir(state_dir: Path) -> Path:
    # Default main agent sessions path used by OpenClaw.
    return state_dir / "agents" / "main" / "sessions"


def pick_latest_session(sessions_dir: Path) -> Path | None:
    if not sessions_dir.exists():
        return None
    candidates = [p for p in sessions_dir.glob("*.jsonl") if p.is_file() and not p.name.endswith(".lock")]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def audit_bootstrap_sizes(workspace_dir: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"workspace_dir": str(workspace_dir), "files": {}, "total_bytes": 0}
    total = 0
    for name in BOOTSTRAP_FILES:
        p = workspace_dir / name
        if p.exists() and p.is_file():
            size = p.stat().st_size
            out["files"][name] = {"exists": True, "bytes": size}
            total += size
        else:
            out["files"][name] = {"exists": False, "bytes": 0}
    out["total_bytes"] = total
    return out


def audit_session_jsonl(session_path: Path, top_n: int = 20) -> dict[str, Any]:
    roles = Counter()
    tool_names = Counter()

    top: list[TopItem] = []

    def consider(chars: int, kind: str, message_id: str, role: str, tool_name: str, preview: str):
        nonlocal top
        ti = TopItem(chars=chars, kind=kind, message_id=message_id, role=role, tool_name=tool_name, preview=preview)
        top.append(ti)

    # Note: we keep this simple (no heap) because jsonl sizes can vary; top_n is small.
    total_lines = 0
    cron_like = 0
    system_like = 0

    with session_path.open("r", encoding="utf-8") as f:
        for line in f:
            total_lines += 1
            line = line.strip("\n")
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue

            if obj.get("type") != "message":
                continue
            msg = obj.get("message") or {}
            role = str(msg.get("role") or "")
            roles[role] += 1

            tool_name = str(msg.get("toolName") or "")
            if tool_name:
                tool_names[tool_name] += 1

            content = msg.get("content") or []
            if not isinstance(content, list):
                continue

            for ci in content:
                if not isinstance(ci, dict):
                    continue
                ctype = ci.get("type")
                if ctype == "text":
                    text = ci.get("text") or ""
                    if not isinstance(text, str) or not text:
                        continue
                    if "System:" in text:
                        system_like += 1
                    if "Cron:" in text:
                        cron_like += 1
                    consider(len(text), "text", str(obj.get("id") or ""), role, tool_name, _preview(text))
                elif ctype == "thinking":
                    think = ci.get("thinking") or ""
                    if not isinstance(think, str) or not think:
                        continue
                    consider(len(think), "thinking", str(obj.get("id") or ""), role, tool_name, _preview(think))

    # Sort by chars desc and truncate
    top.sort(key=lambda x: x.chars, reverse=True)
    top = top[:top_n]

    return {
        "session_path": str(session_path),
        "session_bytes": session_path.stat().st_size if session_path.exists() else 0,
        "total_lines": total_lines,
        "role_counts": dict(roles),
        "tool_counts": dict(tool_names.most_common(20)),
        "system_like_messages": system_like,
        "cron_like_messages": cron_like,
        "top_items": [asdict(t) for t in top],
    }


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description="Audit OpenClaw context bloat sources")
    ap.add_argument("--workspace", default=".", help="Workspace directory (default: current directory)")
    ap.add_argument("--state-dir", default=None, help="Override OpenClaw state dir (default: ~/.openclaw)")
    ap.add_argument("--session", default=None, help="Session JSONL path; if omitted, pick latest in state dir")
    ap.add_argument("--top", type=int, default=20, help="Top N largest content items to report")
    ap.add_argument("--out", default=None, help="Write a JSON report to this path")

    args = ap.parse_args(argv)

    workspace_dir = Path(args.workspace).expanduser().resolve()
    state_dir = Path(args.state_dir).expanduser().resolve() if args.state_dir else find_state_dir()
    sessions_dir = find_sessions_dir(state_dir)

    session_path: Path | None
    if args.session:
        session_path = Path(args.session).expanduser().resolve()
    else:
        session_path = pick_latest_session(sessions_dir)

    report: dict[str, Any] = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workspace": audit_bootstrap_sizes(workspace_dir),
        "state_dir": str(state_dir),
        "sessions_dir": str(sessions_dir),
    }

    if session_path and session_path.exists():
        report["session"] = audit_session_jsonl(session_path, top_n=args.top)
    else:
        report["session"] = {"error": "session not found", "picked": str(session_path) if session_path else None}

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Short stdout summary (keep it compact; do not dump the whole report)
    ws_total = report["workspace"]["total_bytes"]
    print(f"Bootstrap bytes (workspace docs injected each run): {ws_total}")

    sess = report.get("session") or {}
    if "error" in sess:
        print(f"Session audit: {sess['error']}")
        return 0

    print(f"Session: {Path(sess['session_path']).name} ({sess['session_bytes']} bytes)")
    rc = sess.get("role_counts") or {}
    print("Role counts: " + ", ".join([f"{k}={v}" for k, v in rc.items()]))
    print(f"System-like messages: {sess.get('system_like_messages', 0)} | Cron-like: {sess.get('cron_like_messages', 0)}")

    top_items = sess.get("top_items") or []
    if top_items:
        t0 = top_items[0]
        print(
            "Largest item: "
            + f"{t0.get('chars')} chars"
            + f" | role={t0.get('role')}"
            + (f" | tool={t0.get('tool_name')}" if t0.get("tool_name") else "")
            + f" | kind={t0.get('kind')}"
        )

    if args.out:
        print(f"Report written: {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
