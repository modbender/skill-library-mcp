#!/usr/bin/env python3
"""Small wrapper around fredapi for common queries used in this skill.

Requires: FRED_API_KEY in environment.
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
from pathlib import Path

# Fix SSL certificate verification issue
ssl._create_default_https_context = ssl._create_stdlib_context

from fredapi import Fred


ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "references"
TREE_PATH = REFS / "fred_categories_tree.json"
FLAT_PATH = REFS / "fred_categories_flat.json"


def _get_fred() -> Fred:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise SystemExit("Missing FRED_API_KEY in environment")
    return Fred(api_key=api_key)


def _read_json(path: Path):
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")
    return json.loads(path.read_text())


def cmd_category(args: argparse.Namespace) -> int:
    fred = _get_fred()
    df = fred.search_by_category(args.category_id)
    if args.limit:
        df = df.head(args.limit)
    if args.output == "json":
        print(df.to_json(orient="records"))
    else:
        print(df)
    return 0


def cmd_series(args: argparse.Namespace) -> int:
    fred = _get_fred()
    s = fred.get_series(args.series_id)
    if args.tail:
        s = s.tail(args.tail)
    if args.output == "json":
        print(s.to_json())
    else:
        print(s)
    return 0


def cmd_series_info(args: argparse.Namespace) -> int:
    fred = _get_fred()
    info = fred.get_series_info(args.series_id)
    if args.output == "json":
        print(info.to_json())
    else:
        print(info)
    return 0


def cmd_category_path(args: argparse.Namespace) -> int:
    flat = _read_json(FLAT_PATH)
    target = str(args.category_id)
    if target not in flat:
        raise SystemExit(f"category_id not found: {args.category_id}")
    path = []
    cur = flat[target]
    while True:
        path.append(cur["name"])
        parent_id = cur.get("parent_id")
        if parent_id is None or parent_id == -1:
            break
        cur = flat.get(str(parent_id))
        if not cur:
            break
    path_str = " / ".join(reversed(path))
    print(path_str)
    return 0


def cmd_check_category(args: argparse.Namespace) -> int:
    flat = _read_json(FLAT_PATH)
    target = str(args.category_id)
    exists = target in flat
    if not exists:
        print(json.dumps({"exists": False, "children": False, "series": False}))
        return 0

    # check children via flat info
    children_flag = bool(flat[target].get("checked_children"))

    # check series count by calling FRED
    fred = _get_fred()
    try:
        df = fred.search_by_category(args.category_id)
        series_flag = len(df) > 0
    except Exception:
        series_flag = False

    print(json.dumps({"exists": True, "children": children_flag, "series": series_flag}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="FRED helper queries")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_cat = sub.add_parser("category", help="List series under a category")
    p_cat.add_argument("category_id", type=int)
    p_cat.add_argument("--limit", type=int, default=20)
    p_cat.add_argument("--output", choices=["table", "json"], default="table")
    p_cat.set_defaults(func=cmd_category)

    p_ser = sub.add_parser("series", help="Fetch series values")
    p_ser.add_argument("series_id")
    p_ser.add_argument("--tail", type=int, default=20)
    p_ser.add_argument("--output", choices=["table", "json"], default="table")
    p_ser.set_defaults(func=cmd_series)

    p_info = sub.add_parser("series-info", help="Fetch series metadata")
    p_info.add_argument("series_id")
    p_info.add_argument("--output", choices=["table", "json"], default="table")
    p_info.set_defaults(func=cmd_series_info)

    p_path = sub.add_parser("category-path", help="Show full path for a category")
    p_path.add_argument("category_id", type=int)
    p_path.set_defaults(func=cmd_category_path)

    p_chk = sub.add_parser("check-category", help="Check category existence and series")
    p_chk.add_argument("category_id", type=int)
    p_chk.set_defaults(func=cmd_check_category)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
