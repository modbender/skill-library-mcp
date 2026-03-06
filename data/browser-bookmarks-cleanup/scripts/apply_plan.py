"""Apply a cleanup plan to Chrome bookmarks JSON (dry-run or write)."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from _common import (
    chrome_ts_now,
    detect_browser,
    dump_bookmarks,
    load_chrome_bookmarks,
    normalize_name,
    now_iso,
    walk_nodes,
)


def _find_max_numeric_id(data: dict[str, Any]) -> int:
    max_id = 0
    for _, node in walk_nodes(data)[2]["node_by_key"].items():
        try:
            max_id = max(max_id, int(node.get("id", 0)))
        except (ValueError, TypeError):
            pass
    return max_id


def _resolve_selector(selector: dict[str, Any], urls: list, folders: list, indexes: dict) -> str | None:
    nbk = indexes["node_by_key"]
    if root := selector.get("root"):
        return indexes["root_key_by_name"].get(root)
    if guid := selector.get("guid"):
        key = f"guid:{guid}"
        return key if key in nbk else None
    if nid := selector.get("id"):
        key = f"id:{nid}"
        return key if key in nbk else None
    if key := selector.get("key"):
        return key if key in nbk else None
    if path := selector.get("path"):
        cands = [x["key"] for x in urls + folders if x["path"] == path]
        return cands[0] if len(cands) == 1 else None
    if url := selector.get("url"):
        cands = [x["key"] for x in urls if x["url"] == url]
        return cands[0] if len(cands) == 1 else None
    return None


def _is_descendant(node: dict[str, Any], target: dict[str, Any]) -> bool:
    if node is target:
        return True
    for child in node.get("children", []) or []:
        if child.get("type") == "folder" and _is_descendant(child, target):
            return True
    return False


def _apply_operation(data: dict[str, Any], op: dict[str, Any]) -> tuple[bool, str]:
    action = op.get("action")
    if not action:
        return False, "missing action"

    urls, folders, indexes = walk_nodes(data)
    nbk = indexes["node_by_key"]
    pbk = indexes["parent_by_key"]

    def get_nk(field: str) -> tuple[str | None, dict[str, Any] | None]:
        sel = op.get(field)
        if not isinstance(sel, dict):
            return None, None
        key = _resolve_selector(sel, urls, folders, indexes)
        return (key, nbk.get(key)) if key else (None, None)

    if action == "create_folder":
        pk, pnode = get_nk("parent")
        if not pk or not pnode or pnode.get("type") != "folder":
            return False, "create_folder: invalid parent"
        name = normalize_name(op.get("name", ""))
        if not name:
            return False, "create_folder: missing name"
        folder = {
            "type": "folder", "name": name, "id": str(_find_max_numeric_id(data) + 1),
            "guid": str(uuid.uuid4()), "date_added": chrome_ts_now(),
            "date_modified": chrome_ts_now(), "children": [],
        }
        pnode.setdefault("children", []).append(folder)
        pnode["date_modified"] = chrome_ts_now()
        return True, f"created folder '{name}'"

    nk, node = None, None
    if action in {"delete", "rename", "move", "update_url"}:
        nk, node = get_nk("selector")
        if not nk or not node:
            return False, f"{action}: selector not found"
        if nk.startswith("root:"):
            return False, f"{action}: cannot edit root"

    if action == "delete":
        pk = pbk.get(nk)
        parent = nbk.get(pk) if pk else None
        if not parent:
            return False, "delete: parent not found"
        parent["children"] = [c for c in parent.get("children", []) if c is not node]
        parent["date_modified"] = chrome_ts_now()
        return True, f"deleted {nk}"

    if action == "rename":
        new_name = normalize_name(op.get("new_name", ""))
        if not new_name:
            return False, "rename: missing new_name"
        old = node.get("name", "")
        node["name"] = new_name
        return True, f"renamed '{old}' -> '{new_name}'"

    if action == "update_url":
        new_url = op.get("new_url", "").strip()
        if not new_url or node.get("type") != "url":
            return False, "update_url: invalid"
        old = node.get("url", "")
        node["url"] = new_url
        return True, f"updated url '{old}' -> '{new_url}'"

    if action == "move":
        tk, target = get_nk("target")
        if not tk or not target or target.get("type") != "folder":
            return False, "move: invalid target"
        if node.get("type") == "folder" and _is_descendant(node, target):
            return False, "move: circular"
        pk = pbk.get(nk)
        parent = nbk.get(pk) if pk else None
        if not parent:
            return False, "move: parent not found"
        parent["children"] = [c for c in parent.get("children", []) if c is not node]
        target.setdefault("children", []).append(node)
        parent["date_modified"] = chrome_ts_now()
        target["date_modified"] = chrome_ts_now()
        return True, f"moved {nk} -> {tk}"

    return False, f"unsupported action '{action}'"


def run(args: argparse.Namespace) -> int:
    bookmarks_path = Path(args.bookmarks).expanduser()
    if detect_browser(bookmarks_path) == "firefox":
        print("apply-plan only supports Chrome bookmark JSON files.", file=sys.stderr)
        return 1

    data = load_chrome_bookmarks(bookmarks_path)
    plan = json.loads(Path(args.plan).expanduser().read_text(encoding="utf-8"))
    operations = plan.get("operations")
    if not isinstance(operations, list):
        print("Plan must contain an 'operations' array.", file=sys.stderr)
        return 1

    results = []
    applied = failed = 0
    for idx, op in enumerate(operations, 1):
        if not isinstance(op, dict):
            failed += 1
            results.append({"index": idx, "action": None, "status": "failed", "message": "not an object"})
            continue
        ok, msg = _apply_operation(data, op)
        results.append({"index": idx, "action": op.get("action"), "status": "applied" if ok else "failed", "message": msg})
        if ok:
            applied += 1
        else:
            failed += 1

    backup_file = output_file = None
    if args.output:
        output_path = Path(args.output).expanduser()
        dump_bookmarks(output_path, data)
        output_file = str(output_path)
    if args.write:
        backup_file = f"{bookmarks_path}.backup-{int(time.time())}"
        shutil.copy2(bookmarks_path, backup_file)
        dump_bookmarks(bookmarks_path, data)
        output_file = str(bookmarks_path)

    sys.stdout.write(json.dumps({
        "generated_at": now_iso(), "plan_name": plan.get("name"),
        "bookmarks_file": str(bookmarks_path),
        "operations_total": len(operations), "operations_applied": applied,
        "operations_failed": failed, "wrote_output": bool(args.output or args.write),
        "backup_file": backup_file, "output_file": output_file, "results": results,
    }, indent=2, ensure_ascii=False) + "\n")
    return 1 if failed else 0


def add_subparser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("apply-plan", help="Apply cleanup plan to Chrome bookmarks JSON.")
    p.add_argument("--bookmarks", required=True, help="Path to Chrome Bookmarks JSON file.")
    p.add_argument("--plan", required=True, help="Path to plan JSON file.")
    p.add_argument("--output", help="Write modified JSON to this path (dry-run).")
    p.add_argument("--write", action="store_true", help="Write changes with backup.")
    p.set_defaults(func=run)
