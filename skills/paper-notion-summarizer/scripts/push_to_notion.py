#!/usr/bin/env python3
"""Push an LLM-written structured paper summary to Notion.

Input: a JSON file with the following structure:
{
  "title": "Paper Title",
  "metadata": {
    "authors": "...",
    "year": "...",
    "venue": "...",
    "doi": "...",
    "url": "...",
    "source": "arXiv/Crossref"
  },
  "sections": [
    {"heading": "One-line Summary", "content": "..."},
    {"heading": "Problem & Motivation", "content": "..."},
    {"heading": "Key Contributions", "content": "1. ..."},
    {"heading": "Method", "content": "..."},
    {"heading": "Experiments", "content": "..."},
    {"heading": "Ablation & Analysis", "content": "..."},
    {"heading": "Limitations & Future Work", "content": "..."},
    {"heading": "Overall Assessment", "content": "..."}
  ]
}
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests

NOTION_API_VERSION = "2025-09-03"
BLOCK_MAX_TEXT = 1800
CHUNK_BATCH = 80
EMOJI_RE = re.compile(
    "["
    "\U0001F1E6-\U0001F1FF"
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U00002B00-\U00002BFF"
    "\uFE0F"
    "\u200D"
    "]+",
    flags=re.UNICODE,
)

# Metadata heading labels recognized across languages (for dedup)
_META_HEADINGS = {
    "metadata", "0. metadata",
    "메타데이터", "0. 메타데이터",
    "メタデータ", "0. メタデータ",
    "métadonnées", "0. métadonnées",
    "metadaten", "0. metadaten",
}


def _warn(message: str) -> None:
    print(f"[WARN] {message}", file=sys.stderr)


def _sanitize_token(value: str) -> str:
    if not value:
        return ""
    return "".join(ch for ch in value.strip() if 31 < ord(ch) < 127).strip()


def _strip_emoji(text: str) -> str:
    if not text:
        return ""
    cleaned = EMOJI_RE.sub("", text)
    return re.sub(r"\s+", " ", cleaned).strip()


def _read_api_key(override: Optional[str] = None) -> str:
    if override:
        return _sanitize_token(override)
    key = os.environ.get("NOTION_API_KEY")
    if key:
        return _sanitize_token(key)
    key_file = Path.home() / ".config" / "notion" / "api_key"
    if key_file.exists():
        return _sanitize_token(key_file.read_text(encoding="utf-8"))
    return ""


def notion_request(method: str, path: str, token: str, payload: Optional[dict] = None) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }
    url = f"https://api.notion.com/v1{path}"
    r = requests.request(method, url, headers=headers, json=payload, timeout=40)
    if r.status_code >= 400:
        raise RuntimeError(f"Notion API error {r.status_code}: {r.text[:400]}")
    if r.status_code == 204:
        return {}
    return r.json()


def get_block_children(block_id: str, token: str, page_size: int = 100) -> List[dict]:
    cursor = None
    items = []
    while True:
        path = f"/blocks/{block_id}/children?page_size={page_size}"
        if cursor:
            path += f"&start_cursor={cursor}"
        data = notion_request("GET", path, token)
        items.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return items


def clear_block_children(page_id: str, token: str) -> None:
    blocks = get_block_children(page_id, token)
    for block in blocks:
        notion_request("DELETE", f"/blocks/{block['id']}", token)


def append_blocks(page_id: str, token: str, blocks: List[Dict], batch_size: int = CHUNK_BATCH) -> None:
    for i in range(0, len(blocks), batch_size):
        notion_request("PATCH", f"/blocks/{page_id}/children", token, {"children": blocks[i : i + batch_size]})


def _normalize_title(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip().lower()


def search_page_by_title(title: str, token: str) -> Optional[str]:
    payload = {
        "query": title,
        "filter": {"value": "page", "property": "object"},
        "page_size": 10,
    }
    try:
        data = notion_request("POST", "/search", token, payload)
    except Exception:
        data = notion_request("POST", "/search", token, {"query": title, "page_size": 10})

    target = _normalize_title(title)
    for item in data.get("results", []):
        if item.get("object") != "page":
            continue
        try:
            rich = item.get("properties", {}).get("title", {}).get("title", [])
            item_title = "".join([x.get("plain_text", "") for x in rich])
        except Exception:
            item_title = ""
        if item_title and _normalize_title(item_title) == target:
            return item.get("id")
    return None


def chunk_text(text: str, max_len: int = BLOCK_MAX_TEXT) -> List[str]:
    """Split text into Notion-safe chunks, preserving line breaks."""
    if not text:
        return [""]
    text = text.strip()
    if len(text) <= max_len:
        return [text]

    chunks = []
    current = []
    cur_len = 0
    for line in text.split("\n"):
        line_len = len(line) + 1
        if cur_len + line_len > max_len and current:
            chunks.append("\n".join(current))
            current = [line]
            cur_len = line_len
        else:
            current.append(line)
            cur_len += line_len
    if current:
        chunks.append("\n".join(current))
    return chunks


def rich_text_block(text: str, t: str = "paragraph") -> Dict:
    text = text if text else "(No content)"
    return {
        "object": "block",
        "type": t,
        t: {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def heading_block(level: int, text: str) -> Dict:
    level = max(1, min(3, int(level)))
    return {
        "object": "block",
        "type": f"heading_{level}",
        f"heading_{level}": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def divider_block() -> Dict:
    return {"object": "block", "type": "divider", "divider": {}}


def bulleted_list_block(text: str) -> Dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def numbered_list_block(text: str) -> Dict:
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def equation_block(expression: str) -> Dict:
    return {"object": "block", "type": "equation", "equation": {"expression": expression}}


def _parse_content_to_blocks(content: str, heading_level: int = 3, section_heading: str = "") -> List[Dict]:
    """Parse markdown-like content into Notion blocks.

    Supports: numbered/bulleted lists, sub-headings (###), paragraphs, LaTeX equations ($$).
    Programming code fences are converted to plain text with a warning.
    """
    blocks: List[Dict] = []
    lines = content.strip().split("\n")
    math_fence_langs = {"latex", "tex", "math", "equation"}

    i = 0
    paragraph_buffer: List[str] = []

    def flush_paragraph() -> None:
        if paragraph_buffer:
            text = "\n".join(paragraph_buffer).strip()
            if text:
                for chunk in chunk_text(text):
                    blocks.append(rich_text_block(chunk))
            paragraph_buffer.clear()

    def append_equation_or_text(expr: str) -> None:
        expression = expr.strip()
        if not expression:
            return
        if "\n" not in expression and len(expression) <= 1000:
            blocks.append(equation_block(expression))
            return
        rendered = f"$$\n{expression}\n$$" if "\n" in expression else f"$${expression}$$"
        for chunk in chunk_text(rendered):
            blocks.append(rich_text_block(chunk))

    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            flush_paragraph()
            i += 1
            continue

        # Markdown fenced block
        if line.strip().startswith("```"):
            flush_paragraph()
            opening = line.strip()
            fence_lang = opening[3:].strip().lower()
            i += 1
            fence_lines: List[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                fence_lines.append(lines[i].rstrip())
                i += 1
            if i < len(lines) and lines[i].strip().startswith("```"):
                i += 1

            fence_text = "\n".join(fence_lines).strip()
            if fence_lang in math_fence_langs:
                append_equation_or_text(fence_text)
                continue

            _warn(
                f'Code block detected in section="{section_heading or "unknown"}", '
                f'lang="{fence_lang or "plain"}". '
                "Converting to plain text (code blocks are not supported in summaries)."
            )
            if fence_text:
                for chunk in chunk_text(fence_text):
                    blocks.append(rich_text_block(chunk))
            continue

        # Sub-heading
        if line.startswith("### "):
            flush_paragraph()
            blocks.append(heading_block(heading_level, line[4:].strip()))
            i += 1
            continue

        # Numbered list
        m = re.match(r"^\s*(\d+)\.\s+(.+)", line)
        if m:
            flush_paragraph()
            blocks.append(numbered_list_block(m.group(2).strip()))
            i += 1
            continue

        # Bulleted list
        m = re.match(r"^\s*[-*]\s+(.+)", line)
        if m:
            flush_paragraph()
            blocks.append(bulleted_list_block(m.group(1).strip()))
            i += 1
            continue

        # Block equation
        if line.strip().startswith("$$"):
            flush_paragraph()
            stripped = line.strip()
            if stripped.count("$$") >= 2 and stripped != "$$":
                eq_text = stripped.replace("$$", "").strip()
                i += 1
            else:
                eq_lines = [stripped.replace("$$", "")]
                i += 1
                while i < len(lines) and "$$" not in lines[i]:
                    eq_lines.append(lines[i].strip())
                    i += 1
                if i < len(lines):
                    eq_lines.append(lines[i].strip().replace("$$", ""))
                    i += 1
                eq_text = "\n".join(l for l in eq_lines if l).strip()
            append_equation_or_text(eq_text)
            continue

        paragraph_buffer.append(line)
        i += 1

    flush_paragraph()
    return blocks


def build_notion_blocks(summary: Dict) -> List[Dict]:
    """Build Notion blocks from a structured summary JSON."""
    blocks = []
    meta = summary.get("metadata", {})

    # Title heading
    blocks.append(heading_block(1, summary.get("title", "Untitled")))
    blocks.append(divider_block())

    # Metadata section
    blocks.append(heading_block(2, "0. Metadata"))
    meta_lines = [
        f"Authors: {meta.get('authors', 'N/A')}",
        f"Year: {meta.get('year', 'N/A')}",
        f"Venue: {meta.get('venue', 'N/A')}",
    ]
    if meta.get("doi"):
        meta_lines.append(f"DOI: {meta['doi']}")
    if meta.get("url"):
        meta_lines.append(f"URL: {meta['url']}")
    meta_lines.append(f"Collected: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")

    for line in meta_lines:
        blocks.append(bulleted_list_block(line))

    blocks.append(divider_block())

    # Content sections
    visible_idx = 0
    for section in summary.get("sections", []):
        raw_heading = section.get("heading", "") or ""
        heading = _strip_emoji(raw_heading) or "Section"
        if heading != raw_heading:
            _warn(f'Emoji stripped from heading: "{raw_heading}" -> "{heading}"')

        # Skip metadata section if already rendered above
        if heading.lower().strip() in {h.lower() for h in _META_HEADINGS}:
            continue

        visible_idx += 1
        content = section.get("content", "")

        # Strip leading number prefix to avoid double-numbering
        stripped_heading = re.sub(r"^\d+\.\s*", "", heading).strip() or heading

        blocks.append(heading_block(2, f"{visible_idx}. {stripped_heading}"))
        content_blocks = _parse_content_to_blocks(content, section_heading=stripped_heading)
        blocks.extend(content_blocks)
        blocks.append(divider_block())

    return blocks


def create_or_update_page(
    summary: Dict,
    parent_page_id: str,
    token: str,
    force_update: bool = False,
    dry_run: bool = False,
) -> str:
    title = summary.get("title", "Untitled")
    all_blocks = build_notion_blocks(summary)

    if dry_run:
        return json.dumps({"title": title, "block_count": len(all_blocks), "mode": "dry-run"}, ensure_ascii=False, indent=2)

    existing = search_page_by_title(title, token)

    if existing and force_update:
        clear_block_children(existing, token)
        append_blocks(existing, token, all_blocks)
        return existing

    if existing and not force_update:
        append_blocks(existing, token, all_blocks)
        return existing

    payload = {
        "parent": {"page_id": parent_page_id},
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
    }
    page = notion_request("POST", "/pages", token, payload)
    page_id = page.get("id", "")
    append_blocks(page_id, token, all_blocks)
    return page_id


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Push a structured paper summary to Notion")
    p.add_argument("summary_json", help="Path to summary JSON file")
    p.add_argument("--parent-page-id", help="Notion parent page ID")
    p.add_argument("--notion-key", help="Notion API token")
    p.add_argument("--force-update", action="store_true", help="Overwrite existing page content")
    p.add_argument("--dry-run", action="store_true", help="Preview without uploading")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    token = _read_api_key(override=args.notion_key)
    if not token:
        print("NOTION_API_KEY is required")
        return 1

    parent = args.parent_page_id or os.environ.get("NOTION_PARENT_PAGE_ID", "")
    if not parent:
        print("parent page id required: --parent-page-id or NOTION_PARENT_PAGE_ID")
        return 1

    summary_path = Path(args.summary_json)
    if not summary_path.exists():
        print(f"Summary file not found: {summary_path}")
        return 1

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    result = create_or_update_page(summary, parent, token, force_update=args.force_update, dry_run=args.dry_run)

    if args.dry_run:
        print(result)
    else:
        print(f"Notion page created/updated: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
