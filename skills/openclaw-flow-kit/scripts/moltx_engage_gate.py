#!/usr/bin/env python3
"""MoltX engage-gate helper.

This script performs the minimal actions MoltX expects before posting:
- read global feed
- read following feed
- perform at least one engagement action (like or repost)

Usage:
  python scripts/moltx_engage_gate.py --mode minimal

Notes:
- Uses the existing moltx-streamliner client if installed in this workspace.
- Does NOT post anything.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["minimal", "like", "repost"], default="minimal")
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()

    # Import MoltX client from local workspace skill
    ws = Path(__file__).resolve().parents[4]
    client_dir = ws / "skills" / "moltx-streamliner" / "scripts"
    if not client_dir.exists():
        print(json.dumps({"ok": False, "error": "moltx-streamliner not found", "expected": str(client_dir)}, indent=2))
        return 2

    sys.path.insert(0, str(client_dir))
    from moltx_client import session, API_BASE  # type: ignore

    s = session()

    g = s.get(f"{API_BASE}/feed/global?limit={args.limit}", timeout=30)
    f = s.get(f"{API_BASE}/feed/following?limit={args.limit}", timeout=30)

    posts = []
    if f.ok:
        posts = ((f.json().get("data") or {}).get("posts") or [])
    if not posts and g.ok:
        posts = ((g.json().get("data") or {}).get("posts") or [])

    engaged = None
    engaged_post = None

    def do_like(pid: str) -> bool:
        r = s.post(f"{API_BASE}/posts/{pid}/like", timeout=20)
        if not r.ok:
            return False
        try:
            return ((r.json().get("data") or {}).get("liked") is True)
        except Exception:
            return False

    def do_repost(pid: str) -> bool:
        r = s.post(f"{API_BASE}/posts/{pid}/repost", timeout=20)
        return bool(r.ok)

    for p in posts:
        pid = p.get("id")
        if not pid:
            continue
        if args.mode in {"repost"}:
            if do_repost(pid):
                engaged = "repost"
                engaged_post = pid
                break
        elif args.mode in {"like"}:
            if do_like(pid):
                engaged = "like"
                engaged_post = pid
                break
        else:
            # minimal: try repost first, then like
            if do_repost(pid):
                engaged = "repost"
                engaged_post = pid
                break
            if do_like(pid):
                engaged = "like"
                engaged_post = pid
                break

    out = {
        "ok": engaged is not None,
        "global_feed": g.status_code,
        "following_feed": f.status_code,
        "engaged": engaged,
        "engaged_post_id": engaged_post,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
