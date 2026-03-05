#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests


SPEC_URL = "https://api.thrd.email/openapi.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sync_openapi(force: bool):
    skill_root = Path(__file__).resolve().parents[1]
    cache_dir = skill_root / ".cache"
    spec_path = cache_dir / "openapi.json"
    meta_path = cache_dir / "openapi.meta.json"

    meta = load_json(meta_path) or {}
    headers = {}
    if not force:
        etag = meta.get("etag")
        last_modified = meta.get("last_modified")
        if isinstance(etag, str) and etag:
            headers["If-None-Match"] = etag
        if isinstance(last_modified, str) and last_modified:
            headers["If-Modified-Since"] = last_modified

    response = requests.get(SPEC_URL, headers=headers, timeout=30)

    if response.status_code == 304:
        cached_spec = load_json(spec_path)
        if not cached_spec:
            return sync_openapi(force=True)
        version = (cached_spec.get("info") or {}).get("version", "unknown")
        return {
            "ok": True,
            "updated": False,
            "source": "cache",
            "version": version,
            "spec_path": str(spec_path),
            "fetched_at": now_iso(),
        }

    response.raise_for_status()
    spec = response.json()
    version = (spec.get("info") or {}).get("version", "unknown")

    write_json(spec_path, spec)
    write_json(
        meta_path,
        {
            "url": SPEC_URL,
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "version": version,
            "fetched_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "updated": True,
        "source": "network",
        "version": version,
        "spec_path": str(spec_path),
        "fetched_at": now_iso(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Sync THRD OpenAPI contract with ETag support and print current info.version."
    )
    parser.add_argument("--force", action="store_true", help="Ignore cache validators and fetch full document.")
    parser.add_argument(
        "--print-version",
        action="store_true",
        help="Print only info.version (for tool bootstrap checks).",
    )
    args = parser.parse_args()

    try:
        result = sync_openapi(force=args.force)
        if args.print_version:
            print(result["version"])
            return
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
