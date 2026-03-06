#!/usr/bin/env python3
"""
MuPiBox Media DB Manager

Manages MuPiBox data.json through backend API (default http://mupibox:8200).
Creates a local timestamped backup before every mutation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_BASE_URL = "http://mupibox:8200"
DEFAULT_BACKUP_DIR = Path.home() / ".mupibox-db-backups"


@dataclass
class Client:
    base_url: str

    def _get(self, path: str) -> Any:
        req = request.Request(self.base_url.rstrip("/") + path, method="GET")
        with request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)

    def _post(self, path: str, payload: dict[str, Any]) -> str:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.base_url.rstrip("/") + path,
            method="POST",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="replace")

    def get_data(self) -> list[dict[str, Any]]:
        data = self._get("/api/data")
        if not isinstance(data, list):
            raise RuntimeError("/api/data returned non-list payload")
        return data

    def add(self, item: dict[str, Any]) -> str:
        return self._post("/api/add", item)

    def delete(self, index: int) -> str:
        return self._post("/api/delete", {"index": index})

    def edit(self, index: int, item: dict[str, Any]) -> str:
        return self._post("/api/edit", {"index": index, "data": item})





def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def backup_data(data: list[dict[str, Any]], backup_dir: Path, reason: str) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    path = backup_dir / f"data-{now_stamp()}-{reason}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def parse_spotify_url(url: str) -> tuple[str, str]:
    # supports open.spotify.com and spotify: URIs
    url = url.strip()
    m_web = re.search(r"spotify\.com/(album|playlist|show|artist|episode|audiobook)/([A-Za-z0-9]+)", url)
    if m_web:
        return m_web.group(1), m_web.group(2)
    m_uri = re.search(r"spotify:(album|playlist|show|artist|episode|audiobook):([A-Za-z0-9]+)", url)
    if m_uri:
        return m_uri.group(1), m_uri.group(2)
    raise ValueError("Could not parse Spotify URL/URI")


def build_item_from_args(args: argparse.Namespace) -> dict[str, Any]:
    if args.json:
        item = json.loads(args.json)
        if not isinstance(item, dict):
            raise ValueError("--json must contain an object")
        return item

    if not args.type or not args.category:
        raise ValueError("For field-based add, --type and --category are required")

    item: dict[str, Any] = {"type": args.type, "category": args.category}

    for key in ["artist", "title", "query", "id", "playlistid", "artistid", "showid", "audiobookid", "cover"]:
        val = getattr(args, key, None)
        if val is not None:
            item[key] = val

    if args.spotify_url:
        kind, sid = parse_spotify_url(args.spotify_url)
        item["spotify_url"] = args.spotify_url
        if kind == "playlist":
            item["playlistid"] = sid
        elif kind == "artist":
            item["artistid"] = sid
        elif kind == "show":
            item["showid"] = sid
        elif kind in ("album", "episode", "audiobook"):
            item["id"] = sid
            if kind == "audiobook":
                item["audiobookid"] = sid

    return item


def print_items(data: list[dict[str, Any]], limit: int | None = None) -> None:
    shown = data if limit is None else data[:limit]
    for idx, item in enumerate(shown):
        fields = {
            "idx": idx,
            "type": item.get("type"),
            "cat": item.get("category"),
            "artist": item.get("artist"),
            "title": item.get("title"),
            "id": item.get("id") or item.get("playlistid") or item.get("showid") or item.get("artistid"),
        }
        print(json.dumps(fields, ensure_ascii=False))
    if limit is not None and len(data) > limit:
        print(f"... ({len(data) - limit} more)")


def sync_full(client: Client, old: list[dict[str, Any]], new: list[dict[str, Any]]) -> None:
    # 1) edit overlapping indexes where changed
    overlap = min(len(old), len(new))
    for i in range(overlap):
        if old[i] != new[i]:
            out = client.edit(i, new[i])
            if out.strip() not in ("ok", ""):
                raise RuntimeError(f"/api/edit index={i} failed: {out}")

    # 2) delete extra old items from end to start
    for i in range(len(old) - 1, len(new) - 1, -1):
        out = client.delete(i)
        if out.strip() not in ("ok", ""):
            raise RuntimeError(f"/api/delete index={i} failed: {out}")

    # 3) append extra new items
    for i in range(len(old), len(new)):
        out = client.add(new[i])
        if out.strip() not in ("ok", ""):
            raise RuntimeError(f"/api/add index={i} failed: {out}")


def find_index(data: list[dict[str, Any]], *, index: int | None, spotify_id: str | None, title: str | None) -> int:
    if index is not None:
        if not (0 <= index < len(data)):
            raise IndexError(f"index {index} out of range (0..{len(data)-1})")
        return index

    if spotify_id:
        for i, item in enumerate(data):
            if spotify_id in [item.get("id"), item.get("playlistid"), item.get("showid"), item.get("artistid"), item.get("audiobookid")]:
                return i

    if title:
        title_l = title.lower()
        for i, item in enumerate(data):
            if str(item.get("title", "")).lower() == title_l:
                return i

    raise ValueError("No matching item found. Provide --index or a searchable key")


def cmd_list(args: argparse.Namespace) -> None:
    client = Client(args.base_url)
    data = client.get_data()

    if args.filter_type:
        data = [x for x in data if x.get("type") == args.filter_type]
    if args.filter_category:
        data = [x for x in data if x.get("category") == args.filter_category]
    if args.search:
        s = args.search.lower()
        data = [
            x
            for x in data
            if s in json.dumps(x, ensure_ascii=False).lower()
        ]

    if args.raw:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_items(data, args.limit)


def cmd_backup(args: argparse.Namespace) -> None:
    client = Client(args.base_url)
    data = client.get_data()
    bp = backup_data(data, Path(args.backup_dir), "manual")
    print(str(bp))


def cmd_add(args: argparse.Namespace) -> None:
    client = Client(args.base_url)
    data = client.get_data()
    item = build_item_from_args(args)

    bp = backup_data(data, Path(args.backup_dir), "before-add")
    out = client.add(item)
    if out.strip() not in ("ok", ""):
        raise RuntimeError(f"/api/add failed: {out}")

    print(f"OK add. backup={bp}")


def cmd_remove(args: argparse.Namespace) -> None:
    client = Client(args.base_url)
    data = client.get_data()
    idx = find_index(data, index=args.index, spotify_id=args.spotify_id, title=args.title)

    bp = backup_data(data, Path(args.backup_dir), "before-remove")
    out = client.delete(idx)
    if out.strip() not in ("ok", ""):
        raise RuntimeError(f"/api/delete failed: {out}")

    print(f"OK remove index={idx}. backup={bp}")


def cmd_move(args: argparse.Namespace) -> None:
    client = Client(args.base_url)
    old = client.get_data()

    if not (0 <= args.from_index < len(old)):
        raise IndexError("--from out of range")
    if not (0 <= args.to_index < len(old)):
        raise IndexError("--to out of range")

    new = deepcopy(old)
    item = new.pop(args.from_index)
    new.insert(args.to_index, item)

    bp = backup_data(old, Path(args.backup_dir), "before-move")
    sync_full(client, old, new)
    print(f"OK move {args.from_index} -> {args.to_index}. backup={bp}")


def cmd_set(args: argparse.Namespace) -> None:
    client = Client(args.base_url)
    old = client.get_data()
    idx = find_index(old, index=args.index, spotify_id=args.spotify_id, title=args.title)

    new_item = deepcopy(old[idx])
    for kv in args.field:
        if "=" not in kv:
            raise ValueError(f"Invalid --field '{kv}', expected key=value")
        k, v = kv.split("=", 1)
        try:
            parsed = json.loads(v)
        except Exception:
            parsed = v
        new_item[k] = parsed

    bp = backup_data(old, Path(args.backup_dir), "before-set")
    out = client.edit(idx, new_item)
    if out.strip() not in ("ok", ""):
        raise RuntimeError(f"/api/edit failed: {out}")

    print(f"OK set index={idx}. backup={bp}")


def cmd_restore(args: argparse.Namespace) -> None:
    backup_path = Path(args.file)
    if not backup_path.exists():
        raise FileNotFoundError(str(backup_path))

    new = json.loads(backup_path.read_text(encoding="utf-8"))
    if not isinstance(new, list):
        raise ValueError("Backup file is not a JSON list")

    client = Client(args.base_url)
    old = client.get_data()
    bp = backup_data(old, Path(args.backup_dir), "before-restore")
    sync_full(client, old, new)
    print(f"OK restore from {backup_path}. safety-backup={bp}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Manage MuPiBox media database via API")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--backup-dir", default=str(DEFAULT_BACKUP_DIR))

    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list", help="List entries")
    pl.add_argument("--type", dest="filter_type")
    pl.add_argument("--category", dest="filter_category")
    pl.add_argument("--search")
    pl.add_argument("--limit", type=int, default=50)
    pl.add_argument("--raw", action="store_true")
    pl.set_defaults(func=cmd_list)

    pb = sub.add_parser("backup", help="Create manual backup")
    pb.set_defaults(func=cmd_backup)

    pa = sub.add_parser("add", help="Add one entry")
    pa.add_argument("--json", help="Raw JSON object")
    pa.add_argument("--type")
    pa.add_argument("--category")
    pa.add_argument("--artist")
    pa.add_argument("--title")
    pa.add_argument("--query")
    pa.add_argument("--id")
    pa.add_argument("--playlistid")
    pa.add_argument("--artistid")
    pa.add_argument("--showid")
    pa.add_argument("--audiobookid")
    pa.add_argument("--cover")
    pa.add_argument("--spotify-url")
    pa.set_defaults(func=cmd_add)

    pr = sub.add_parser("remove", help="Remove one entry")
    pr.add_argument("--index", type=int)
    pr.add_argument("--spotify-id")
    pr.add_argument("--title")
    pr.set_defaults(func=cmd_remove)

    pm = sub.add_parser("move", help="Move entry to a new index")
    pm.add_argument("--from", dest="from_index", type=int, required=True)
    pm.add_argument("--to", dest="to_index", type=int, required=True)
    pm.set_defaults(func=cmd_move)

    ps = sub.add_parser("set", help="Edit fields on an entry")
    ps.add_argument("--index", type=int)
    ps.add_argument("--spotify-id")
    ps.add_argument("--title")
    ps.add_argument("--field", action="append", required=True, help="key=value (value may be JSON)")
    ps.set_defaults(func=cmd_set)

    prest = sub.add_parser("restore", help="Restore full DB from backup JSON")
    prest.add_argument("--file", required=True)
    prest.set_defaults(func=cmd_restore)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except error.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
