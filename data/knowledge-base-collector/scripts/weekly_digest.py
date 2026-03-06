#!/usr/bin/env python3
"""Prepare a weekly digest from KB entries (last N days).

This script DOES NOT call an LLM. It selects and structures candidates so an agent
(or you) can quickly write a weekly summary.

Outputs:
- counts by source
- top tags
- top entries (newest / best-tagged)

Usage:
  python3 weekly_digest.py --days 7 --limit 30
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

KB_DEFAULT = "/home/ubuntu/.openclaw/kb"
INDEX_REL = "20_Inbox/urls/index.jsonl"


def parse_iso(s: str) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def load_index(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
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
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()

    kb_root = Path(os.environ.get("KB_ROOT", KB_DEFAULT))
    idx = kb_root / INDEX_REL
    recs = load_index(idx)

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=args.days)

    items: List[Dict[str, Any]] = []
    for r in recs:
        created = parse_iso(r.get("createdAt") or "")
        if created and created >= cutoff:
            items.append(r)

    items.sort(key=lambda x: x.get("createdAt", ""), reverse=True)

    by_source = Counter([r.get("source") or "unknown" for r in items])

    # tag stats
    tag_counter = Counter()
    for r in items:
        for t in (r.get("tags") or []):
            if t.startswith("#source:") or t.startswith("#type:") or t.startswith("#lang:"):
                continue
            tag_counter[t] += 1

    print(f"window={args.days}d count={len(items)}")
    print("\n[sources]")
    for k, v in by_source.most_common():
        print(f"- {k}: {v}")

    print("\n[top_tags]")
    for t, c in tag_counter.most_common(20):
        print(f"- {t}: {c}")

    print("\n[entries]")
    for r in items[: max(0, args.limit)]:
        title = r.get("title") or "(untitled)"
        url = r.get("url")
        tags = " ".join((r.get("tags") or [])[:12])
        print("---")
        print("title:", title)
        print("createdAt:", r.get("createdAt"))
        print("source:", r.get("source"), "status:", r.get("status"))
        print("tags:", tags)
        print("path:", r.get("path"))
        if url:
            print("url:", url)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
