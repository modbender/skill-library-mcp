"""Shared constants, URL/timestamp helpers, SQLite utilities, and tree walking."""

from __future__ import annotations

import json
import sqlite3
import shutil
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import parse

# --- Constants ---

CHROME_EPOCH_OFFSET_US = 11644473600000000
TRACKING_PARAMS = {
    "gclid", "fbclid", "igshid", "mc_cid", "mc_eid", "mkt_tok", "ref", "ref_src",
}
WEAK_NAMES = {"", "untitled", "bookmark", "new bookmark"}
BROWSER_ROOTS = {
    "chrome": "~/Library/Application Support/Google/Chrome",
    "firefox": "~/Library/Application Support/Firefox",
}
_FF_TYPE_BOOKMARK = 1
_FF_TYPE_FOLDER = 2


# --- Timestamp helpers ---

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def chrome_ts_now() -> str:
    return str(int(time.time() * 1_000_000) + CHROME_EPOCH_OFFSET_US)


def chrome_ts_to_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        unix_us = int(value) - CHROME_EPOCH_OFFSET_US
    except (TypeError, ValueError):
        return None
    if unix_us <= 0:
        return None
    return datetime.fromtimestamp(unix_us / 1_000_000, tz=timezone.utc)


def firefox_ts_to_dt(value: int | None) -> datetime | None:
    if not value or value <= 0:
        return None
    return datetime.fromtimestamp(value / 1_000_000, tz=timezone.utc)


def ts_to_dt(value: str | int | None, browser: str) -> datetime | None:
    if browser == "firefox":
        return firefox_ts_to_dt(int(value) if value else None)
    return chrome_ts_to_dt(str(value) if value else None)


# --- URL helpers ---

def normalize_name(name: str) -> str:
    return (name or "").strip()


def clean_host(host: str) -> str:
    return host.lower().strip(".")


def maybe_registrable_domain(host: str) -> str:
    parts = clean_host(host).split(".")
    if len(parts) <= 2:
        return clean_host(host)
    return ".".join(parts[-2:])


def normalize_url(url: str, drop_query: bool = False, drop_fragment: bool = True) -> str:
    try:
        parsed = parse.urlsplit(url)
    except ValueError:
        return ""
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"}:
        return ""
    netloc = clean_host(parsed.hostname or "")
    if not netloc:
        return ""
    port = parsed.port
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{netloc}:{port}"
    path = parsed.path or "/"
    query = ""
    if not drop_query:
        pairs = parse.parse_qsl(parsed.query, keep_blank_values=True)
        pairs.sort()
        query = parse.urlencode(pairs, doseq=True)
    fragment = "" if drop_fragment else parsed.fragment
    return parse.urlunsplit((scheme, netloc, path, query, fragment))


def normalize_url_without_tracking(url: str) -> str:
    try:
        parsed = parse.urlsplit(url)
    except ValueError:
        return ""
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"}:
        return ""
    netloc = clean_host(parsed.hostname or "")
    if not netloc:
        return ""
    path = parsed.path or "/"
    kept = []
    for key, value in parse.parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower().startswith("utm_") or key.lower() in TRACKING_PARAMS:
            continue
        kept.append((key, value))
    kept.sort()
    return parse.urlunsplit((scheme, netloc, path, parse.urlencode(kept, doseq=True), ""))


def has_tracking_params(url: str) -> bool:
    try:
        parsed = parse.urlsplit(url)
    except ValueError:
        return False
    for key, _ in parse.parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower().startswith("utm_") or key.lower() in TRACKING_PARAMS:
            return True
    return False


# --- SQLite helpers ---

# Track temp files created for locked-db fallback copies.
_sqlite_tmp_files: dict[int, Path] = {}


def open_sqlite_ro(path: Path) -> sqlite3.Connection:
    """Try read-only first, fall back to a temp copy if locked."""
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        conn.execute("SELECT 1")
        return conn
    except sqlite3.Error:
        pass
    tmp = tempfile.NamedTemporaryFile(prefix="db-copy-", suffix=".sqlite", delete=False)
    tmp_path = Path(tmp.name)
    tmp.close()
    shutil.copy2(path, tmp_path)
    conn = sqlite3.connect(str(tmp_path))
    _sqlite_tmp_files[id(conn)] = tmp_path
    return conn


def close_sqlite(conn: sqlite3.Connection) -> None:
    tmp_path = _sqlite_tmp_files.pop(id(conn), None)
    conn.close()
    if tmp_path:
        tmp_path.unlink(missing_ok=True)


# --- Bookmark loading ---

def load_chrome_bookmarks(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_bookmarks(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_firefox_bookmarks(places_path: Path) -> dict[str, Any]:
    """Read Firefox places.sqlite and return a Chrome-compatible bookmark structure."""
    import uuid
    conn = open_sqlite_ro(places_path)
    try:
        rows = conn.execute(
            "SELECT b.id, b.type, b.fk, b.parent, b.title, b.dateAdded, b.guid, "
            "p.url FROM moz_bookmarks b LEFT JOIN moz_places p ON b.fk = p.id"
        ).fetchall()
    finally:
        close_sqlite(conn)

    nodes_by_id: dict[int, dict[str, Any]] = {}
    children_map: dict[int, list[int]] = defaultdict(list)

    for row_id, btype, fk, parent, title, date_added, guid, url in rows:
        node: dict[str, Any] = {
            "id": str(row_id),
            "guid": guid or str(uuid.uuid4()),
            "name": normalize_name(title or ""),
            "date_added": str(date_added or 0),
        }
        if btype == _FF_TYPE_FOLDER:
            node["type"] = "folder"
            node["children"] = []
        elif btype == _FF_TYPE_BOOKMARK and url:
            node["type"] = "url"
            node["url"] = url
        else:
            continue
        nodes_by_id[row_id] = node
        if parent:
            children_map[parent].append(row_id)

    for parent_id, child_ids in children_map.items():
        parent_node = nodes_by_id.get(parent_id)
        if parent_node and parent_node.get("type") == "folder":
            parent_node["children"] = [nodes_by_id[cid] for cid in child_ids if cid in nodes_by_id]

    root_map = {"toolbar": "bookmark_bar", "menu": "other", "unfiled": "synced"}
    roots: dict[str, Any] = {}
    for node in nodes_by_id.values():
        if node.get("type") != "folder":
            continue
        name_lower = node["name"].lower()
        for ff_name, chrome_equiv in root_map.items():
            if ff_name in name_lower and chrome_equiv not in roots:
                roots[chrome_equiv] = node
                break
    if not roots:
        top_ids = set(nodes_by_id.keys()) - {cid for cids in children_map.values() for cid in cids}
        for tid in top_ids:
            node = nodes_by_id[tid]
            if node.get("type") == "folder":
                roots[node["name"] or f"root_{tid}"] = node

    return {"roots": roots}


def detect_browser(bookmarks_path: Path) -> str:
    return "firefox" if bookmarks_path.suffix == ".sqlite" else "chrome"


def load_bookmarks_auto(path: Path) -> tuple[dict[str, Any], str]:
    browser = detect_browser(path)
    if browser == "firefox":
        return load_firefox_bookmarks(path), "firefox"
    return load_chrome_bookmarks(path), "chrome"


# --- Tree walking ---

def node_key(node: dict[str, Any]) -> str:
    if guid := node.get("guid"):
        return f"guid:{guid}"
    if nid := node.get("id"):
        return f"id:{nid}"
    return f"node:{id(node)}"


def walk_nodes(data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    roots = data.get("roots", {})
    urls: list[dict[str, Any]] = []
    folders: list[dict[str, Any]] = []
    indexes = {"node_by_key": {}, "parent_by_key": {}, "path_by_key": {}, "root_key_by_name": {}}

    def visit(node: dict[str, Any], path_parts: list[str], parent_key: str | None, root_name: str) -> None:
        nkey = node_key(node)
        indexes["node_by_key"][nkey] = node
        if parent_key is not None:
            indexes["parent_by_key"][nkey] = parent_key
        node_path = "/" + "/".join(path_parts) if path_parts else "/"
        indexes["path_by_key"][nkey] = node_path

        ntype = node.get("type")
        if ntype == "url":
            urls.append({
                "key": nkey, "guid": node.get("guid"), "id": node.get("id"),
                "name": normalize_name(node.get("name", "")),
                "url": node.get("url", ""), "path": node_path,
                "root": root_name, "date_added": node.get("date_added"),
            })
        elif ntype == "folder":
            children = node.get("children", []) or []
            folders.append({
                "key": nkey, "guid": node.get("guid"), "id": node.get("id"),
                "name": normalize_name(node.get("name", "")),
                "path": node_path, "root": root_name,
                "child_count": len(children), "date_added": node.get("date_added"),
                "is_root": nkey.startswith("root:"),
            })
            for child in children:
                visit(child, path_parts + [normalize_name(child.get("name", "")) or "<unnamed>"], nkey, root_name)

    for root_name, root_node in roots.items():
        if root_name == "custom_root" or not isinstance(root_node, dict):
            continue
        rkey = f"root:{root_name}"
        root_node = dict(root_node)
        root_node.setdefault("type", "folder")
        root_node.setdefault("name", root_name)
        roots[root_name] = root_node
        indexes["root_key_by_name"][root_name] = rkey
        indexes["node_by_key"][rkey] = root_node
        indexes["path_by_key"][rkey] = f"/{root_name}"
        for child in root_node.get("children", []) or []:
            visit(child, [root_name, normalize_name(child.get("name", "")) or "<unnamed>"], rkey, root_name)
        folders.append({
            "key": rkey, "guid": root_node.get("guid"), "id": root_node.get("id"),
            "name": root_name, "path": f"/{root_name}", "root": root_name,
            "child_count": len(root_node.get("children", []) or []),
            "date_added": root_node.get("date_added"), "is_root": True,
        })

    return urls, folders, indexes


def bookmark_projection(item: dict[str, Any]) -> dict[str, Any]:
    return {k: item.get(k) for k in ("key", "guid", "id", "name", "url", "path")}


def folder_projection(item: dict[str, Any]) -> dict[str, Any]:
    return {k: item.get(k) for k in ("key", "guid", "id", "name", "path", "child_count")}
