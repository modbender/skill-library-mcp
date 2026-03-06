#!/usr/bin/env python3
"""Apply JSONL records to DIY_PC Notion tables.

Reads JSONL from stdin. Each record:
  {
    "target": "enclosure"|"storage"|"pcconfig"|"pcinput",
    "title": "...",                 # optional (for creation)
    "properties": { ... },           # values as simple scalars
    "overwrite": false               # optional; default false
  }

This script is intentionally *dumb* and deterministic: it does NOT parse raw text.
Use the agent/LLM to classify + extract, then call this script.

Notion API:
- Query/schema via data_sources
- Create rows via pages with parent.database_id
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass

API = "https://api.notion.com/v1"

DEFAULT_NOTION_VERSION = "2025-09-03"

# Runtime-initialized configuration (loaded once at startup)
CONFIG = {}
IDS = {}

DEFAULT_IDS = {
    # Public-safe defaults (no real IDs). Users must provide IDs via config.
    "pcconfig": {
        "data_source_id": None,
        "database_id": None,
        "title_prop": "Name",
        "key": ("Name", "Purchase Date"),
    },
    "pcinput": {
        "data_source_id": None,
        "database_id": None,
        "title_prop": "名前",
        "key": ("型番", "Serial", "名前"),
    },
    "storage": {
        "data_source_id": None,
        "database_id": None,
        "title_prop": "Name",
        "key": ("シリアル",),
    },
    "enclosure": {
        "data_source_id": None,
        "database_id": None,
        "title_prop": "Name",
        "key": ("取り外し表示名", "Name"),
    },
}


def load_config() -> dict:
    """Load config from JSON.

    Order:
    1) DIY_PC_INGEST_CONFIG (path)
    2) ~/.config/diy-pc-ingest/config.json

    Config schema example: skills/diy-pc-ingest/references/config.example.json
    """
    p = os.environ.get("DIY_PC_INGEST_CONFIG")
    if not p:
        p = os.path.expanduser("~/.config/diy-pc-ingest/config.json")
    if not os.path.exists(p):
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f) or {}


def notion_version(cfg: dict) -> str:
    return (
        (cfg.get("notion") or {}).get("version")
        or os.environ.get("NOTION_VERSION")
        or DEFAULT_NOTION_VERSION
    )


def notion_api_key(cfg: dict) -> str:
    # Prefer env
    tok = os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")
    if tok:
        return tok.strip()

    # Config inline token
    tok = ((cfg.get("notion") or {}).get("api_key") or "").strip()
    if tok and "PUT_YOUR_" not in tok:
        return tok

    # Legacy local file path (author setup)
    key_path = os.environ.get("NOTION_API_KEY_FILE") or "~/.config/notion/api_key"
    return open(os.path.expanduser(key_path), "r", encoding="utf-8").read().strip()


def ids(cfg: dict) -> dict:
    t = ((cfg.get("notion") or {}).get("targets") or {})
    if not t:
        return DEFAULT_IDS

    out = {}
    for k, v in t.items():
        if not isinstance(v, dict):
            continue
        out[k] = {
            "data_source_id": v.get("data_source_id"),
            "database_id": v.get("database_id"),
            "title_prop": v.get("title_prop") or "Name",
            "key": tuple(v.get("key") or []),
        }
    # Keep defaults for any missing targets
    for k, v in DEFAULT_IDS.items():
        out.setdefault(k, v)
    return out


# Initialize global config + targets
CONFIG = load_config()
IDS = ids(CONFIG)


def req(method: str, path: str, body: dict | None = None) -> dict:
    url = API + path
    cfg = load_config()
    headers = {
        "Authorization": f"Bearer {notion_api_key(cfg)}",
        "Notion-Version": notion_version(cfg),
    }
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(url, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code} {path}: {raw}")
    return json.loads(raw) if raw else {}


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def build_prop(schema_prop: dict, value):
    t = schema_prop.get("type")
    if t == "title":
        return {"title": [{"type": "text", "text": {"content": str(value)}}]}
    if t == "rich_text":
        return {"rich_text": [{"type": "text", "text": {"content": str(value)}}]}
    if t == "number":
        return {"number": float(value) if value is not None else None}
    if t == "date":
        return {"date": {"start": str(value)}}
    if t == "checkbox":
        return {"checkbox": bool(value)}
    if t == "select":
        return {"select": {"name": str(value)}} if value is not None and str(value) != "" else {"select": None}
    if t == "status":
        return {"status": {"name": str(value)}} if value is not None and str(value) != "" else {"status": None}
    if t == "multi_select":
        # value can be list[str] or comma-separated string
        if isinstance(value, str):
            names = [v.strip() for v in value.split(",") if v.strip()]
        else:
            names = [str(v).strip() for v in (value or []) if str(v).strip()]
        return {"multi_select": [{"name": n} for n in names]}
    if t == "relation":
        # expects list of page ids
        ids = value if isinstance(value, list) else []
        return {"relation": [{"id": pid} for pid in ids]}
    # fallback
    return None


def require_ids(target: str, cfg: dict):
    t = IDS.get(target) or {}
    missing = []
    if not t.get("data_source_id"):
        missing.append(f"{target}.data_source_id")
    if not t.get("database_id"):
        missing.append(f"{target}.database_id")
    if missing:
        cfg_path = os.environ.get("DIY_PC_INGEST_CONFIG") or "~/.config/diy-pc-ingest/config.json"
        raise RuntimeError(
            "Missing Notion IDs in config: "
            + ", ".join(missing)
            + ". Set them in "
            + cfg_path
            + " (see references/config.example.json)."
        )


def get_schema(data_source_id: str) -> dict:
    return req("GET", f"/data_sources/{data_source_id}")


def query_by_title(data_source_id: str, title_prop: str, contains: str, page_size: int = 5) -> list[dict]:
    body = {
        "page_size": page_size,
        "filter": {"property": title_prop, "title": {"contains": contains}},
    }
    j = req("POST", f"/data_sources/{data_source_id}/query", body)
    return j.get("results", []) or []


def query_by_rich_text(data_source_id: str, prop: str, contains: str, page_size: int = 5) -> list[dict]:
    body = {
        "page_size": page_size,
        "filter": {"property": prop, "rich_text": {"contains": contains}},
    }
    j = req("POST", f"/data_sources/{data_source_id}/query", body)
    return j.get("results", []) or []


def _prop_plain_text(prop: dict) -> str:
    if not prop:
        return ""
    t = prop.get("type")
    if t in ("title", "rich_text"):
        arr = prop.get(t) or []
        return "".join([(x.get("plain_text") or "") for x in arr]).strip()
    return ""


def _prop_date_start(prop: dict) -> str | None:
    if not prop or prop.get("type") != "date":
        return None
    d = prop.get("date") or {}
    return d.get("start")


def _prop_number(prop: dict):
    if not prop or prop.get("type") != "number":
        return None
    return prop.get("number")


def find_existing(target: str, schema: dict, props_in: dict) -> dict | None:
    """Best-effort upsert matching.

    Primary keys are in IDS[target]['key'].

    Notion doesn't enforce unique constraints, so we implement matching here.

    Behavior:
    - If the configured key is composite (2+ properties) and all values are present,
      we query by the first property and then narrow in-memory by exact matches.
    - If the key is not composite or values are missing, we fall back to per-property
      matching (legacy behavior).

    If multiple rows match, return None (caller should avoid creation by providing a stronger key).
    """

    cfg = IDS[target]
    ds = cfg["data_source_id"]
    sch_props = schema.get("properties") or {}

    def get_value_from_row(row: dict, prop_name: str):
        props = row.get("properties") or {}
        prop = props.get(prop_name)
        if not prop:
            return None
        t = prop.get("type")
        if t in ("title", "rich_text"):
            return _prop_plain_text(prop)
        if t == "date":
            return _prop_date_start(prop)
        if t == "number":
            return _prop_number(prop)
        if t == "select":
            return (prop.get("select") or {}).get("name")
        if t == "status":
            return (prop.get("status") or {}).get("name")
        return None

    # 1) composite key handling (if all values present)
    key_props = list(cfg.get("key") or [])
    if len(key_props) >= 2 and all(props_in.get(k) for k in key_props):
        first = key_props[0]
        first_schema = sch_props.get(first) or {}
        first_type = first_schema.get("type")
        first_val = normalize(str(props_in.get(first)))
        if first_type == "title":
            hits = query_by_title(ds, first, first_val, page_size=25)
        elif first_type == "rich_text":
            hits = query_by_rich_text(ds, first, first_val, page_size=25)
        else:
            hits = []

        def matches(row: dict) -> bool:
            for k in key_props:
                want = props_in.get(k)
                if want is None or want == "":
                    return False
                got = get_value_from_row(row, k)
                # Normalize texty fields
                if isinstance(want, str):
                    want_n = normalize(want)
                else:
                    want_n = str(want)
                if isinstance(got, str):
                    got_n = normalize(got)
                else:
                    got_n = str(got) if got is not None else None
                if got_n != want_n:
                    return False
            return True

        narrowed = [r for r in hits if matches(r)]
        if len(narrowed) == 1:
            return narrowed[0]
        return None

    # 2) legacy: try key properties one-by-one (works for single-key tables)
    for key_prop in key_props:
        v = props_in.get(key_prop)
        if not v:
            continue
        v = normalize(str(v))
        if not v:
            continue
        schema_prop = sch_props.get(key_prop)
        if not schema_prop:
            continue
        t = schema_prop.get("type")
        if t == "rich_text":
            hits = query_by_rich_text(ds, key_prop, v, page_size=10)
        elif t == "title":
            hits = query_by_title(ds, key_prop, v, page_size=10)
        else:
            continue
        if len(hits) == 1:
            return hits[0]
        # If multiple, don't guess.

    # 2) storage-specific safe fallback: match by title + (optional) purchase date/price
    if target == "storage":
        title = props_in.get("Name") or props_in.get("名前")
        if not title:
            return None
        title = normalize(str(title))
        hits = query_by_title(ds, cfg["title_prop"], title, page_size=10)
        if not hits:
            return None

        # Optional disambiguation
        want_date = props_in.get("購入日")
        want_price = props_in.get("価格(円)")

        def ok(r: dict) -> bool:
            props = r.get("properties") or {}
            if want_date:
                got = _prop_date_start(props.get("購入日"))
                if got != str(want_date):
                    return False
            if want_price is not None:
                got = _prop_number(props.get("価格(円)"))
                try:
                    if got is None or float(got) != float(want_price):
                        return False
                except Exception:
                    return False
            return True

        narrowed = [r for r in hits if ok(r)]
        if len(narrowed) == 1:
            return narrowed[0]

        # If there is exactly one hit and it has empty serial, accept (post-fill pattern)
        if len(hits) == 1:
            props = hits[0].get("properties") or {}
            serial_plain = _prop_plain_text(props.get("シリアル"))
            if not serial_plain:
                return hits[0]

    return None


def build_patch(schema: dict, incoming: dict, existing_props: dict, overwrite: bool) -> dict:
    out = {}
    sch_props = schema.get("properties") or {}

    for k, v in incoming.items():
        if k not in sch_props:
            continue
        schema_prop = sch_props[k]
        # Only patch missing fields unless overwrite
        if not overwrite:
            ep = (existing_props or {}).get(k)
            if ep:
                et = ep.get("type")
                if et in ("rich_text", "title"):
                    arr = ep.get(et) or []
                    if any((x.get("plain_text") or "").strip() for x in arr):
                        continue
                elif et == "number" and ep.get("number") is not None:
                    continue
                elif et == "date" and (ep.get("date") or {}).get("start"):
                    continue
                elif et == "checkbox" and ep.get("checkbox") is True:
                    continue
                elif et == "select" and (ep.get("select") or {}).get("name"):
                    continue
                elif et == "status" and (ep.get("status") or {}).get("name"):
                    continue
                elif et == "multi_select" and (ep.get("multi_select") or []):
                    continue
                elif et == "relation" and (ep.get("relation") or []):
                    continue
        built = build_prop(schema_prop, v)
        if built is not None:
            out[k] = built

    return out


def create_page(target: str, schema: dict, title: str, properties: dict) -> dict:
    cfg = IDS[target]
    title_prop = cfg["title_prop"]
    sch_props = schema.get("properties") or {}

    out_props = {}
    if title:
        if title_prop in sch_props:
            out_props[title_prop] = build_prop(sch_props[title_prop], title)
        else:
            # fallback to Name
            if "Name" in sch_props:
                out_props["Name"] = build_prop(sch_props["Name"], title)

    for k, v in properties.items():
        if k == title_prop:
            continue
        if k not in sch_props:
            continue
        built = build_prop(sch_props[k], v)
        if built is not None:
            out_props[k] = built

    body = {
        "parent": {"database_id": cfg["database_id"]},
        "properties": out_props,
    }
    return req("POST", "/pages", body)


def main():
    records = [json.loads(line) for line in sys.stdin.read().splitlines() if line.strip()]
    if not records:
        print("NO_RECORDS")
        return

    cache_schema = {}

    summary = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
    outputs = []

    for rec in records:
        target = rec.get("target")
        if target not in IDS:
            summary["errors"] += 1
            outputs.append({"error": f"unknown target: {target}", "record": rec})
            continue

        # Ensure config contains the necessary Notion IDs
        require_ids(target, CONFIG)

        overwrite = bool(rec.get("overwrite", False))
        page_id = rec.get("page_id") or rec.get("id")
        archive = bool(rec.get("archive", False) or rec.get("archived", False))

        title = rec.get("title") or rec.get("properties", {}).get("Name") or rec.get("properties", {}).get("名前")
        props_in = rec.get("properties") or {}

        if target not in cache_schema:
            cache_schema[target] = get_schema(IDS[target]["data_source_id"])
        schema = cache_schema[target]

        # Escape hatch: update a specific page by id (used for manual cleanup / de-dup).
        if page_id:
            existing_page = req("GET", f"/pages/{page_id}")
            patch = build_patch(schema, props_in, existing_page.get("properties") or {}, overwrite)
            body = {}
            if patch:
                body["properties"] = patch
            if archive:
                body["archived"] = True
            if body:
                updated = req("PATCH", f"/pages/{page_id}", body)
                summary["updated"] += 1
                outputs.append({"action": "updated", "target": target, "id": updated.get("id"), "url": updated.get("url")})
            else:
                summary["skipped"] += 1
                outputs.append({"action": "skipped", "target": target, "id": existing_page.get("id"), "url": existing_page.get("url")})
            continue

        existing = find_existing(target, schema, props_in)
        if existing:
            patch = build_patch(schema, props_in, existing.get("properties") or {}, overwrite)
            if patch:
                updated = req("PATCH", f"/pages/{existing['id']}", {"properties": patch})
                summary["updated"] += 1
                outputs.append({"action": "updated", "target": target, "id": updated.get("id"), "url": updated.get("url")})
            else:
                summary["skipped"] += 1
                outputs.append({"action": "skipped", "target": target, "id": existing.get("id"), "url": existing.get("url")})
        else:
            created = create_page(target, schema, str(title or "(untitled)"), props_in)
            summary["created"] += 1
            outputs.append({"action": "created", "target": target, "id": created.get("id"), "url": created.get("url")})

        # Optional: mirror storage items into PCConfig as an installed component record.
        # This keeps a per-PC parts list in addition to the per-device storage table.
        if target == "storage" and rec.get("mirror_to_pcconfig"):
            pc = props_in.get("現在の接続先PC")
            purchase_date = props_in.get("購入日")
            name = props_in.get("Name")
            if not (pc and purchase_date and name):
                summary["skipped"] += 1
                outputs.append({"action": "skipped", "target": "pcconfig", "reason": "mirror_missing_fields", "need": ["現在の接続先PC", "購入日", "Name"], "got": {"現在の接続先PC": bool(pc), "購入日": bool(purchase_date), "Name": bool(name)}})
            else:
                pc_rec = {
                    "target": "pcconfig",
                    "title": str(name),
                    "properties": {
                        "PC": pc,
                        "Category": "ストレージ",
                        "Name": str(name),
                        "Purchase Date": str(purchase_date),
                        "Purchase Vendor": props_in.get("購入店"),
                        "Purchase Price": props_in.get("価格(円)"),
                        "Spec": f"S/N: {props_in.get('シリアル','')}",
                        "Installed": True,
                        "Active": True,
                        "Notes": "mirrored from storage",
                    },
                    "overwrite": False,
                }
                # Recurse through the same logic once (no further mirroring)
                pc_schema = cache_schema.get("pcconfig") or get_schema(IDS["pcconfig"]["data_source_id"])
                cache_schema["pcconfig"] = pc_schema
                pc_existing = find_existing("pcconfig", pc_schema, pc_rec["properties"])
                if pc_existing:
                    pc_patch = build_patch(pc_schema, pc_rec["properties"], pc_existing.get("properties") or {}, False)
                    if pc_patch:
                        pc_updated = req("PATCH", f"/pages/{pc_existing['id']}", {"properties": pc_patch})
                        summary["updated"] += 1
                        outputs.append({"action": "updated", "target": "pcconfig", "id": pc_updated.get("id"), "url": pc_updated.get("url"), "reason": "mirrored"})
                    else:
                        summary["skipped"] += 1
                        outputs.append({"action": "skipped", "target": "pcconfig", "id": pc_existing.get("id"), "url": pc_existing.get("url"), "reason": "mirrored_no_changes"})
                else:
                    pc_created = create_page("pcconfig", pc_schema, str(name), pc_rec["properties"])
                    summary["created"] += 1
                    outputs.append({"action": "created", "target": "pcconfig", "id": pc_created.get("id"), "url": pc_created.get("url"), "reason": "mirrored"})

    print(json.dumps({"summary": summary, "results": outputs}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
