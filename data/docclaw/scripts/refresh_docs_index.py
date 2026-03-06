#!/usr/bin/env python3
"""Build a local OpenClaw docs index from docs.openclaw.ai sources.

Sources:
- <docs-root>/llms.txt
- <docs-root>/sitemap.xml
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_DOCS_ROOT = "https://docs.openclaw.ai"
TRUSTED_DOCS_HOST = "docs.openclaw.ai"
SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUT_JSON = SKILL_DIR / "references" / "openclaw-docs-index.json"
DEFAULT_OUT_MD = SKILL_DIR / "references" / "openclaw-docs-index.md"
UA = "docclaw/1.0.3"

BULLET_RE = re.compile(
    r"^\s*-\s+\[(?P<title>[^\]]+)\]\((?P<url>https://docs\.openclaw\.ai/[^)]+)\)(?::\s*(?P<desc>.*))?$"
)


def http_get(url: str, timeout: float) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error while fetching {url}: {exc}") from exc
    return data.decode("utf-8", errors="replace")


def normalize_docs_root(value: str) -> str:
    parsed = urllib.parse.urlparse(value.strip())
    if parsed.scheme != "https" or parsed.netloc != TRUSTED_DOCS_HOST:
        raise ValueError(f"docs-root must be https://{TRUSTED_DOCS_HOST}")
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def normalize_url(url: str, docs_root: str) -> tuple[str, str, str, str]:
    """Return markdown_url, html_url, path, section."""
    normalized = url.strip()
    if normalized.endswith(".md"):
        markdown_url = normalized
        html_url = normalized[:-3]
    else:
        html_url = normalized
        markdown_url = f"{normalized}.md"

    parsed = urllib.parse.urlparse(html_url)
    path = parsed.path.lstrip("/") or "index"
    section = path.split("/", 1)[0] if "/" in path else path

    if not html_url.startswith(docs_root):
        html_url = f"{docs_root}/{path}".rstrip("/")
        markdown_url = f"{html_url}.md"

    return markdown_url, html_url, path, section


def title_from_path(path: str) -> str:
    leaf = (path.strip("/").split("/")[-1] or "index").replace(".md", "")
    return leaf.replace("-", " ").replace("_", " ").title()


def parse_llms(llms_text: str, docs_root: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for raw in llms_text.splitlines():
        m = BULLET_RE.match(raw.strip())
        if not m:
            continue
        title = m.group("title").strip()
        url = m.group("url").strip()
        desc = (m.group("desc") or "").strip()
        markdown_url, html_url, path, section = normalize_url(url, docs_root)
        entries.append(
            {
                "title": title,
                "description": desc,
                "markdown_url": markdown_url,
                "html_url": html_url,
                "path": path,
                "section": section,
                "source": "llms",
            }
        )
    return entries


def parse_sitemap(xml_text: str) -> dict[str, str]:
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise RuntimeError(f"Invalid sitemap XML: {exc}") from exc

    out: dict[str, str] = {}
    for url_el in root.findall("sm:url", ns):
        loc_el = url_el.find("sm:loc", ns)
        mod_el = url_el.find("sm:lastmod", ns)
        if loc_el is None or not loc_el.text:
            continue
        out[loc_el.text.strip()] = (mod_el.text or "").strip() if mod_el is not None else ""
    return out


def write_index_md(path: Path, payload: dict) -> None:
    lines: list[str] = []
    lines.append("# OpenClaw Docs Index")
    lines.append("")
    lines.append(f"Generated: {payload['generated_at']}")
    lines.append(f"Entries: {len(payload['entries'])}")
    lines.append("")
    lines.append("Sources:")
    lines.append(f"- {payload['sources']['llms']}")
    lines.append(f"- {payload['sources']['sitemap']}")
    lines.append("")
    lines.append("## Entries")
    lines.append("")

    for entry in payload["entries"]:
        lastmod = entry.get("lastmod") or "n/a"
        desc = entry.get("description") or ""
        source = entry.get("source") or "unknown"
        suffix = f" - {desc}" if desc else ""
        lines.append(
            f"- `{entry['path']}` - [{entry['title']}]({entry['html_url']}) (source: {source}, lastmod: {lastmod}){suffix}"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_index(docs_root: str, timeout: float) -> dict:
    llms_url = f"{docs_root}/llms.txt"
    sitemap_url = f"{docs_root}/sitemap.xml"

    llms_text = http_get(llms_url, timeout)
    sitemap_text = http_get(sitemap_url, timeout)

    llms_entries = parse_llms(llms_text, docs_root)
    sitemap_map = parse_sitemap(sitemap_text)

    dedup: dict[str, dict] = {}

    for item in llms_entries:
        key = item["path"]
        if key in dedup:
            continue
        html = item["html_url"]
        md = item["markdown_url"]
        item["lastmod"] = sitemap_map.get(html, "") or sitemap_map.get(md, "")
        dedup[key] = item

    for loc, lastmod in sitemap_map.items():
        if not loc.startswith(docs_root):
            continue
        markdown_url, html_url, path, section = normalize_url(loc, docs_root)
        if path in dedup:
            continue
        dedup[path] = {
            "title": title_from_path(path),
            "description": "",
            "markdown_url": markdown_url,
            "html_url": html_url,
            "path": path,
            "section": section,
            "source": "sitemap",
            "lastmod": lastmod,
        }

    entries = sorted(dedup.values(), key=lambda x: x["path"])

    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "docs_root": docs_root,
        "sources": {"llms": llms_url, "sitemap": sitemap_url},
        "stats": {
            "llms_entries": len(llms_entries),
            "sitemap_entries": len(sitemap_map),
            "indexed_entries": len(entries),
        },
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh local OpenClaw docs index")
    parser.add_argument("--docs-root", default=DEFAULT_DOCS_ROOT, help="Docs root URL")
    parser.add_argument("--out-json", default=str(DEFAULT_OUT_JSON), help="Output JSON path")
    parser.add_argument("--out-md", default=str(DEFAULT_OUT_MD), help="Output Markdown path")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds")
    args = parser.parse_args()

    try:
        docs_root = normalize_docs_root(args.docs_root)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    payload = build_index(docs_root, args.timeout)

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_index_md(out_md, payload)

    print(f"Wrote JSON: {out_json}")
    print(f"Wrote Markdown: {out_md}")
    print(f"Indexed entries: {payload['stats']['indexed_entries']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
