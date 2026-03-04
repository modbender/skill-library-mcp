#!/usr/bin/env python3
"""Build category path index from fred_categories_flat.json.

Outputs references/category_paths.json
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "references"
FLAT_PATH = REFS / "fred_categories_flat.json"
OUT_PATH = REFS / "category_paths.json"


def load_flat() -> dict:
    if not FLAT_PATH.exists():
        raise SystemExit(f"Missing required file: {FLAT_PATH}")
    return json.loads(FLAT_PATH.read_text())


def build_path(flat: dict, cid: int) -> str:
    cur = flat.get(str(cid))
    if not cur:
        return ""
    parts = []
    while True:
        parts.append(cur.get("name", ""))
        parent_id = cur.get("parent_id")
        if parent_id is None or parent_id == -1:
            break
        cur = flat.get(str(parent_id))
        if not cur:
            break
    return " / ".join(reversed([p for p in parts if p]))


def main() -> int:
    flat = load_flat()
    out = {}
    for cid_str, info in flat.items():
        try:
            cid = int(info.get("id", cid_str))
        except Exception:
            continue
        name = info.get("name", "")
        path = build_path(flat, cid)
        out[str(cid)] = {"id": cid, "name": name, "path": path}

    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT_PATH} with {len(out)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
