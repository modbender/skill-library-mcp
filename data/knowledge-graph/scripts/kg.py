#!/usr/bin/env python3
"""kg.py — deterministic helpers for Clawdbot's file-based knowledge graph.

Data model:
- Workspace-relative root: life/areas/
- Entity path: life/areas/<kind>/<slug>/
- items.json: JSON array of atomic facts
- summary.md: short snapshot derived from active facts

This script is intentionally dependency-free (stdlib only).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]  # .../skills/knowledge-graph
# workspace root is one more up
WORKSPACE_ROOT = WORKSPACE_ROOT.parent  # .../clawd
KG_ROOT = WORKSPACE_ROOT / "life" / "areas"

ID_RE = re.compile(r"^(?P<prefix>[a-z0-9-]+)-(?P<num>\d{3})$")


def today_date() -> str:
    return _dt.date.today().isoformat()


def now_iso() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def norm_entity(entity: str) -> Tuple[str, str]:
    """Parse `people/safa` into (kind, slug)."""
    entity = entity.strip().strip("/")
    parts = [p for p in entity.split("/") if p]
    if len(parts) != 2:
        raise SystemExit(f"--entity must be like 'people/safa' (got {entity!r})")
    kind, slug = parts
    if not re.fullmatch(r"[a-z0-9-]+", kind):
        raise SystemExit(f"Invalid kind {kind!r} (use [a-z0-9-]+)")
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise SystemExit(f"Invalid slug {slug!r} (use [a-z0-9-]+)")
    return kind, slug


def entity_dir(kind: str, slug: str) -> Path:
    return KG_ROOT / kind / slug


def load_items(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text("utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON in {path}: {e}")
    if not isinstance(data, list):
        raise SystemExit(f"items.json must be a JSON array: {path}")
    for i, it in enumerate(data):
        if not isinstance(it, dict):
            raise SystemExit(f"items.json entry {i} is not an object: {path}")
    return data


def write_items(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", "utf-8")


def next_id(slug: str, items: List[Dict[str, Any]]) -> str:
    max_num = 0
    for it in items:
        raw = str(it.get("id", ""))
        m = ID_RE.match(raw)
        if not m:
            continue
        if m.group("prefix") != slug:
            continue
        max_num = max(max_num, int(m.group("num")))
    return f"{slug}-{max_num + 1:03d}"


def add_fact(
    *,
    kind: str,
    slug: str,
    fact: str,
    category: str,
    source: str,
    timestamp: str,
) -> str:
    ed = entity_dir(kind, slug)
    items_path = ed / "items.json"
    items = load_items(items_path)

    new_id = next_id(slug, items)
    item = {
        "id": new_id,
        "fact": fact.strip(),
        "category": category,
        "timestamp": timestamp,
        "source": source,
        "status": "active",
        "supersededBy": None,
    }
    items.append(item)
    write_items(items_path, items)
    return new_id


def supersede_fact(
    *,
    kind: str,
    slug: str,
    old_id: str,
    new_fact: str,
    category: str,
    source: str,
    timestamp: str,
) -> str:
    ed = entity_dir(kind, slug)
    items_path = ed / "items.json"
    items = load_items(items_path)

    # find old
    old = None
    for it in items:
        if it.get("id") == old_id:
            old = it
            break
    if old is None:
        raise SystemExit(f"Could not find old id {old_id!r} in {items_path}")

    new_id = next_id(slug, items)
    new_item = {
        "id": new_id,
        "fact": new_fact.strip(),
        "category": category,
        "timestamp": timestamp,
        "source": source,
        "status": "active",
        "supersededBy": None,
    }

    # mark old
    old["status"] = "superseded"
    old["supersededBy"] = new_id

    items.append(new_item)
    write_items(items_path, items)
    return new_id


def build_summary(kind: str, slug: str, items: List[Dict[str, Any]], max_lines: int = 12) -> str:
    active = [it for it in items if it.get("status") == "active"]

    # stable-ish ordering: newest first by timestamp, then id
    def sort_key(it: Dict[str, Any]):
        ts = str(it.get("timestamp") or "")
        return (ts, str(it.get("id") or ""))

    active.sort(key=sort_key, reverse=True)

    lines = [f"# {slug}", "", f"Updated: {today_date()}", ""]
    for it in active[:max_lines]:
        fact = str(it.get("fact") or "").strip()
        if not fact:
            continue
        lines.append(f"- {fact}")

    if len(active) > max_lines:
        lines.append(f"- …and {len(active) - max_lines} more active facts")

    lines.append("")
    return "\n".join(lines)


def summarize_entity(kind: str, slug: str) -> Path:
    ed = entity_dir(kind, slug)
    items_path = ed / "items.json"
    items = load_items(items_path)

    summary = build_summary(kind, slug, items)
    out = ed / "summary.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(summary, "utf-8")
    return out


def main() -> None:
    p = argparse.ArgumentParser(prog="kg.py")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add an active fact to an entity")
    p_add.add_argument("--entity", required=True, help="e.g. people/safa")
    p_add.add_argument("--fact", required=True)
    p_add.add_argument("--category", required=True)
    p_add.add_argument("--source", default="conversation")
    p_add.add_argument("--timestamp", default=today_date())
    p_add.add_argument("--summarize", action="store_true", help="Also regenerate summary.md")

    p_sup = sub.add_parser("supersede", help="Supersede an old fact by id and add a new one")
    p_sup.add_argument("--entity", required=True)
    p_sup.add_argument("--old", required=True, dest="old_id")
    p_sup.add_argument("--fact", required=True, dest="new_fact")
    p_sup.add_argument("--category", required=True)
    p_sup.add_argument("--source", default="conversation")
    p_sup.add_argument("--timestamp", default=today_date())
    p_sup.add_argument("--summarize", action="store_true")

    p_sum = sub.add_parser("summarize", help="Regenerate summary.md from active facts")
    p_sum.add_argument("--entity", required=True)

    args = p.parse_args()

    kind, slug = norm_entity(args.entity)

    if args.cmd == "add":
        new_id = add_fact(
            kind=kind,
            slug=slug,
            fact=args.fact,
            category=args.category,
            source=args.source,
            timestamp=args.timestamp,
        )
        if args.summarize:
            summarize_entity(kind, slug)
        print(new_id)
        return

    if args.cmd == "supersede":
        new_id = supersede_fact(
            kind=kind,
            slug=slug,
            old_id=args.old_id,
            new_fact=args.new_fact,
            category=args.category,
            source=args.source,
            timestamp=args.timestamp,
        )
        if args.summarize:
            summarize_entity(kind, slug)
        print(new_id)
        return

    if args.cmd == "summarize":
        out = summarize_entity(kind, slug)
        print(str(out))
        return

    raise SystemExit(f"Unknown cmd: {args.cmd}")


if __name__ == "__main__":
    main()
