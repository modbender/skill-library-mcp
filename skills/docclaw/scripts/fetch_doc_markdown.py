#!/usr/bin/env python3
"""Fetch a specific OpenClaw docs page as Markdown (.md endpoint)."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_DOCS_ROOT = "https://docs.openclaw.ai"
TRUSTED_DOCS_HOST = "docs.openclaw.ai"
SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = SKILL_DIR / "references" / "openclaw-docs-index.json"
DEFAULT_CACHE_DIR = SKILL_DIR / "references" / "cache"
UA = "docclaw/1.0.3"


def http_get(url: str, timeout: float) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    return data.decode("utf-8", errors="replace")


def normalize_docs_root(value: str) -> str:
    parsed = urllib.parse.urlparse(value.strip())
    if parsed.scheme != "https" or parsed.netloc != TRUSTED_DOCS_HOST:
        raise ValueError(f"docs-root must be https://{TRUSTED_DOCS_HOST}")
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def normalize_markdown_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme != "https" or parsed.netloc != TRUSTED_DOCS_HOST:
        return ""
    path = parsed.path or ""
    if not path:
        return ""
    if not path.endswith(".md"):
        path = f"{path}.md"
    return f"https://{TRUSTED_DOCS_HOST}{path}"


def slugify(value: str) -> str:
    v = value.strip().lower()
    v = re.sub(r"[^a-z0-9/_-]+", "-", v)
    v = v.strip("-/")
    return v or "index"


def load_index(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = payload.get("entries", [])
        if isinstance(entries, list):
            return [e for e in entries if isinstance(e, dict)]
    except Exception:
        return []
    return []


def resolve_target(query: str, entries: list[dict], docs_root: str) -> tuple[str, str]:
    q = query.strip()
    if q.startswith("http://") or q.startswith("https://"):
        raise ValueError("Full URLs are not allowed. Pass a docs slug like cli/models.")

    raw_slug = q.strip("/").removesuffix(".md")
    for e in entries:
        if raw_slug and e.get("path") == raw_slug:
            md_url = normalize_markdown_url(str(e.get("markdown_url", "")))
            if md_url:
                return md_url, slugify(str(e["path"]))

    q_lower = q.lower()
    for e in entries:
        title = str(e.get("title", "")).lower()
        if q_lower and q_lower in title:
            md_url = normalize_markdown_url(str(e.get("markdown_url", "")))
            if md_url:
                return md_url, slugify(str(e.get("path", q_lower)))

    guess = slugify(raw_slug)
    return f"{docs_root}/{guess}.md", guess


def suggest_targets(query: str, entries: list[dict], limit: int = 5) -> list[str]:
    universe = [str(e.get("path", "")) for e in entries if e.get("path")]
    universe.extend([str(e.get("title", "")) for e in entries if e.get("title")])
    universe = sorted({u for u in universe if u})

    q = query.strip().removesuffix(".md")
    if not q or not universe:
        return []
    return difflib.get_close_matches(q, universe, n=limit, cutoff=0.5)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch an OpenClaw docs page as markdown")
    parser.add_argument("target", help="Doc slug (e.g. cli/models) or title keyword")
    parser.add_argument("--docs-root", default=DEFAULT_DOCS_ROOT, help="Docs root URL")
    parser.add_argument("--index", default=str(DEFAULT_INDEX), help="Index JSON path")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="Cache output directory")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds")
    parser.add_argument("--out", default="", help="Output file path (optional)")
    args = parser.parse_args()

    try:
        docs_root = normalize_docs_root(args.docs_root)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    entries = load_index(Path(args.index))
    try:
        md_url, slug = resolve_target(args.target, entries, docs_root)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    md_url = normalize_markdown_url(md_url)
    if not md_url:
        raise SystemExit(f"Resolved URL is outside trusted docs host ({TRUSTED_DOCS_HOST}).")

    try:
        markdown = http_get(md_url, args.timeout)
    except urllib.error.HTTPError as exc:
        suggestions = suggest_targets(args.target, entries)
        msg = [f"Failed to fetch {md_url} (HTTP {exc.code})."]
        if suggestions:
            msg.append("Suggestions:")
            msg.extend([f"- {s}" for s in suggestions])
        raise SystemExit("\n".join(msg)) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error while fetching {md_url}: {exc}") from exc

    if "<html" in markdown[:500].lower():
        raise SystemExit(
            f"Fetched HTML instead of markdown from {md_url}. Try another slug or refresh the index first."
        )

    out_path = Path(args.out) if args.out else Path(args.cache_dir) / f"{slug}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")

    print(f"Fetched: {md_url}")
    print(f"Saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
