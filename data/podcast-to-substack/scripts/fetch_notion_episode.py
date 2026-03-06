#!/usr/bin/env python3
"""Fetch a podcast episode page from Notion and export text + images.

- Resolves page by episode number/title from a Notion data source.
- Recursively traverses child blocks (handles nested lists/toggles/callouts).
- Extracts image URLs and downloads them immediately to local files.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
USER_AGENT = "podcast-to-substack-notion-fetcher/1.0"


def env_api_key() -> str:
    key = os.getenv("NOTION_API_KEY", "").strip()
    if key:
        return key
    key_file = Path.home() / ".config" / "notion" / "api_key"
    if key_file.exists():
        return key_file.read_text(encoding="utf-8").strip()
    raise RuntimeError("Missing NOTION_API_KEY and ~/.config/notion/api_key")


def api_request(method: str, path: str, key: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=f"{API}{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {key}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Notion API error {exc.code} on {path}: {details}") from exc


def find_title_property(schema: dict[str, Any]) -> str:
    for name, prop in schema.items():
        if isinstance(prop, dict) and prop.get("type") == "title":
            return name
    return "Name"


def candidate_episode_props(schema: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for name, prop in schema.items():
        ptype = prop.get("type") if isinstance(prop, dict) else None
        lname = name.lower()
        if ptype in {"number", "rich_text", "title"} and ("episode" in lname or lname in {"ep", "ep #", "ep#"}):
            names.append(name)
    return names


def query_datasource(key: str, ds_id: str, query_text: str) -> dict[str, Any]:
    # Pull schema so we can construct a robust filter for this workspace.
    schema_resp = api_request("GET", f"/data_sources/{ds_id}", key)
    props = schema_resp.get("properties", {}) if isinstance(schema_resp, dict) else {}

    title_prop = find_title_property(props)
    ep_props = candidate_episode_props(props)

    filters: list[dict[str, Any]] = []
    if query_text.isdigit():
        filters.append({"property": title_prop, "title": {"contains": query_text}})
        for ep_name in ep_props:
            prop_type = props.get(ep_name, {}).get("type")
            if prop_type == "number":
                filters.append({"property": ep_name, "number": {"equals": int(query_text)}})
            elif prop_type == "rich_text":
                filters.append({"property": ep_name, "rich_text": {"contains": query_text}})
    else:
        filters.append({"property": title_prop, "title": {"contains": query_text}})

    payload: dict[str, Any] = {"page_size": 25}
    if filters:
        payload["filter"] = {"or": filters} if len(filters) > 1 else filters[0]

    return api_request("POST", f"/data_sources/{ds_id}/query", key, payload)


def score_page(page: dict[str, Any], query_text: str) -> tuple[int, str]:
    props = page.get("properties", {})
    title = "Untitled"
    for p in props.values():
        if isinstance(p, dict) and p.get("type") == "title":
            title = "".join(t.get("plain_text", "") for t in p.get("title", [])) or "Untitled"
            break

    s = 0
    q = query_text.lower().strip()
    t = title.lower()
    if q and q in t:
        s += 20
    if q.isdigit() and re.search(rf"(?:episode\s+)?#?{re.escape(q)}\b", t):
        s += 80

    for name, p in props.items():
        if not isinstance(p, dict):
            continue
        ptype = p.get("type")
        lname = name.lower()
        if "episode" not in lname and lname not in {"ep", "ep #", "ep#"}:
            continue
        if ptype == "number" and q.isdigit() and p.get("number") == int(q):
            s += 100
        elif ptype == "rich_text":
            txt = "".join(x.get("plain_text", "") for x in p.get("rich_text", []))
            if q and q in txt.lower():
                s += 50

    return s, title


def choose_page(results: list[dict[str, Any]], query_text: str) -> tuple[dict[str, Any], str]:
    if not results:
        raise RuntimeError("No matching page found in Notion data source")
    ranked = sorted(((score_page(p, query_text), p) for p in results), key=lambda x: x[0][0], reverse=True)
    top_score, top_title = ranked[0][0]
    if top_score <= 0:
        # Fall back to first result if scoring is weak.
        p = results[0]
        fallback_title = score_page(p, query_text)[1]
        return p, fallback_title
    return ranked[0][1], top_title


def list_children(key: str, block_id: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cursor = None
    while True:
        qs = "?page_size=100"
        if cursor:
            qs += "&start_cursor=" + urllib.parse.quote(cursor)
        resp = api_request("GET", f"/blocks/{block_id}/children{qs}", key)
        results = resp.get("results", [])
        out.extend(results)
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return out


def walk_blocks_recursive(key: str, root_id: str) -> list[dict[str, Any]]:
    all_blocks: list[dict[str, Any]] = []

    def walk(parent_id: str) -> None:
        for block in list_children(key, parent_id):
            all_blocks.append(block)
            if block.get("has_children"):
                walk(block.get("id"))

    walk(root_id)
    return all_blocks


def rich_text_text(block: dict[str, Any], field: str) -> str:
    node = block.get(field, {})
    rich = node.get("rich_text", []) if isinstance(node, dict) else []
    return "".join(item.get("plain_text", "") for item in rich).strip()


def extract_script_text(blocks: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for b in blocks:
        btype = b.get("type")
        if btype == "paragraph":
            txt = rich_text_text(b, "paragraph")
        elif btype in {"heading_1", "heading_2", "heading_3"}:
            txt = rich_text_text(b, btype)
        elif btype == "bulleted_list_item":
            base = rich_text_text(b, "bulleted_list_item")
            txt = f"• {base}" if base else ""
        elif btype == "numbered_list_item":
            base = rich_text_text(b, "numbered_list_item")
            txt = f"- {base}" if base else ""
        elif btype == "quote":
            base = rich_text_text(b, "quote")
            txt = f"> {base}" if base else ""
        elif btype == "callout":
            txt = rich_text_text(b, "callout")
        elif btype == "toggle":
            txt = rich_text_text(b, "toggle")
        else:
            txt = ""
        if txt:
            lines.append(txt)
    return "\n".join(lines).strip()


def extract_image_urls(page: dict[str, Any], blocks: list[dict[str, Any]]) -> list[str]:
    urls: list[str] = []

    # 1) Inline image blocks.
    for b in blocks:
        if b.get("type") != "image":
            continue
        image = b.get("image", {})
        itype = image.get("type")
        if itype == "file":
            u = image.get("file", {}).get("url")
        elif itype == "external":
            u = image.get("external", {}).get("url")
        else:
            u = None
        if u:
            urls.append(u)

    # 2) Files properties on the page (covers thumbnail/cover-type properties).
    props = page.get("properties", {})
    for p in props.values():
        if not isinstance(p, dict) or p.get("type") != "files":
            continue
        for item in p.get("files", []):
            itype = item.get("type")
            if itype == "file":
                u = item.get("file", {}).get("url")
            elif itype == "external":
                u = item.get("external", {}).get("url")
            else:
                u = None
            if u:
                urls.append(u)

    # Deduplicate while preserving order.
    seen: set[str] = set()
    ordered: list[str] = []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        ordered.append(u)
    return ordered


def infer_ext(url: str, content_type: str | None) -> str:
    if content_type:
        guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if guessed:
            return guessed
    parsed = urllib.parse.urlparse(url)
    path_ext = Path(parsed.path).suffix
    if path_ext:
        return path_ext
    return ".jpg"


def download_images(urls: list[str], out_dir: Path) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    local_paths: list[str] = []
    for idx, u in enumerate(urls, start=1):
        req = urllib.request.Request(u, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                content = resp.read()
                ext = infer_ext(u, resp.headers.get("Content-Type"))
        except Exception as exc:  # pragma: no cover - best effort download
            print(f"warning: failed to download image {u}: {exc}", file=sys.stderr)
            continue
        out_path = out_dir / f"podcast-image-{idx:02d}{ext}"
        out_path.write_bytes(content)
        local_paths.append(str(out_path))
    return local_paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch episode content + images from Notion")
    parser.add_argument("query", help="Episode number or title keyword")
    parser.add_argument("--download-dir", default="/tmp/podcast-to-substack-images", help="Directory for downloaded images")
    parser.add_argument("--no-download", action="store_true", help="Skip downloading image URLs")
    args = parser.parse_args()

    try:
        key = env_api_key()
        ds_id = (os.getenv("NOTION_DATA_SOURCE_ID") or os.getenv("NOTION_DATABASE_ID") or "").strip()
        if not ds_id:
            raise RuntimeError("Set NOTION_DATA_SOURCE_ID or NOTION_DATABASE_ID")

        query_resp = query_datasource(key, ds_id, args.query)
        results = query_resp.get("results", [])
        page, title = choose_page(results, args.query)
        page_id = page.get("id")
        if not page_id:
            raise RuntimeError("Matched page missing id")

        blocks = walk_blocks_recursive(key, page_id)
        script = extract_script_text(blocks)
        image_urls = extract_image_urls(page, blocks)
        image_paths: list[str] = []
        if not args.no_download and image_urls:
            image_paths = download_images(image_urls, Path(args.download_dir) / str(page_id))

        out = {
            "page_id": page_id,
            "title": title,
            "script": script,
            "image_urls": image_urls,
            "image_paths": image_paths,
            "apple_podcasts_link": os.getenv(
                "APPLE_PODCASTS_URL",
                "https://podcasts.apple.com/ca/podcast/the-canadian-real-estate-investor/id1634197127",
            ),
        }
        print(json.dumps(out, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
