#!/usr/bin/env python3
"""Search KB entries (index.jsonl + content.md).

Examples:
  python3 search_kb.py --q "claude code" 
  python3 search_kb.py --tags "#claude-code #coding-agent" --limit 20
  python3 search_kb.py --source x --since 30d --q "agent"

Notes:
- This is a lightweight grep-style search. For large KBs, upgrade to sqlite FTS.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

KB_DEFAULT = "/home/ubuntu/.openclaw/kb"
INDEX_REL = "20_Inbox/urls/index.jsonl"


def parse_since(s: str) -> Optional[dt.datetime]:
    s = (s or "").strip().lower()
    if not s:
        return None
    m = re.fullmatch(r"(\d+)([dhm])", s)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2)
    delta = {"m": dt.timedelta(minutes=n), "h": dt.timedelta(hours=n), "d": dt.timedelta(days=n)}[unit]
    return dt.datetime.now(dt.timezone.utc) - delta


def load_index(idx_path: Path) -> List[Dict[str, Any]]:
    if not idx_path.exists():
        return []
    out = []
    for line in idx_path.read_text(encoding="utf-8", errors="ignore").splitlines():
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


def text_match(path: Path, pat: re.Pattern[str]) -> bool:
    try:
        if not path.exists():
            return False
        txt = path.read_text(encoding="utf-8", errors="ignore")
        return bool(pat.search(txt))
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", default="", help="keyword/regex (case-insensitive)")
    ap.add_argument("--tags", default="", help='space-separated tags, e.g. "#ai #agent"')
    ap.add_argument("--source", default="", help="x|web|wechat|image")
    ap.add_argument("--since", default="", help="e.g. 7d / 24h / 30m")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()

    kb_root = Path(os.environ.get("KB_ROOT", KB_DEFAULT))
    idx = kb_root / INDEX_REL
    records = load_index(idx)

    q = args.q.strip()
    pat = re.compile(q, re.I) if q else None

    need_tags = [t for t in args.tags.split() if t.startswith("#")]
    need_source = args.source.strip().lower() or None
    since_dt = parse_since(args.since)

    hits: List[Tuple[Dict[str, Any], str]] = []

    for rec in records:
        if need_source and (rec.get("source") != need_source):
            continue
        if need_tags:
            tags = rec.get("tags") or []
            if any(t not in tags for t in need_tags):
                continue
        if since_dt:
            # createdAt is ISO; compare lexicographically is OK for Z times, but parse for safety
            created = rec.get("createdAt") or ""
            try:
                cd = dt.datetime.fromisoformat(created.replace("Z", "+00:00"))
                if cd < since_dt:
                    continue
            except Exception:
                pass

        if pat:
            title = rec.get("title") or ""
            url = rec.get("url") or ""
            if pat.search(title) or pat.search(url):
                hits.append((rec, "title/url"))
            else:
                p = rec.get("path")
                if p:
                    if text_match(Path(p) / "content.md", pat):
                        hits.append((rec, "content"))
        else:
            hits.append((rec, "filter"))

    # newest first
    hits.sort(key=lambda x: x[0].get("createdAt", ""), reverse=True)

    out = hits[: max(args.limit, 0)]
    print(f"count={len(out)}")
    for rec, why in out:
        print("---")
        print("title:", rec.get("title"))
        print("source:", rec.get("source"), "status:", rec.get("status"))
        print("tags:", " ".join((rec.get("tags") or [])[:20]))
        print("createdAt:", rec.get("createdAt"))
        print("path:", rec.get("path"))
        print("url:", rec.get("url"))
        print("matched:", why)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
