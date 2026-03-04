#!/usr/bin/env python3
"""List WeChat items that are blocked and need refetch.

Find entries from index.jsonl where:
- source == 'wechat'
- status == 'blocked_verification'
- tag includes '#needs-manual'

Outputs a concise list for Telegram.

Usage:
  python3 wechat_backlog.py --limit 30
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List

KB_DEFAULT = "/home/ubuntu/.openclaw/kb"
INDEX_REL = "20_Inbox/urls/index.jsonl"


def load_index(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    # keep last record per key
    last: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for rec in out:
        k = rec.get("key")
        if not k:
            continue
        if k not in last:
            order.append(k)
        last[k] = rec
    return [last[k] for k in order]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()

    kb_root = Path(os.environ.get("KB_ROOT", KB_DEFAULT))
    idx = kb_root / INDEX_REL
    recs = load_index(idx)

    blocked = []
    for r in recs:
        if r.get("source") != "wechat":
            continue
        if r.get("status") != "blocked_verification":
            continue
        tags = r.get("tags") or []
        if "#needs-manual" not in tags:
            continue
        blocked.append(r)

    # newest first
    blocked.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    blocked = blocked[: max(0, args.limit)]

    print(f"count={len(blocked)}")
    for r in blocked:
        print("---")
        print("title:", r.get("title"))
        print("createdAt:", r.get("createdAt"))
        print("path:", r.get("path"))
        print("url:", r.get("url"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
