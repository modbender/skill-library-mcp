#!/usr/bin/env python3
"""Unified KB ingest (MVP)

Goal: One entrypoint for URLs (X/WeChat/web) with tag-first storage into the shared OpenClaw KB.

What it does (MVP):
- Detects source by URL host:
  - x.com / twitter.com: fetch via r.jina.ai proxy (best success without login)
  - mp.weixin.qq.com: try direct fetch; if verification page -> create placeholder entry with status
  - other: web_fetch-like readability is not available in this offline script, so we use r.jina.ai as a generic fallback
- Writes per-item folder with content.md + meta.json
- Appends index.jsonl
- Basic de-dup by URL hash key (skips if key already exists in index)

Usage:
  python3 kb_ingest.py <url> [--tags "#a #b"] [--note "..."]

Env:
  KB_ROOT: defaults to /home/ubuntu/.openclaw/kb

Note: Images/screenshots are not handled in this script (needs OCR/vision tool). We'll add later.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

import requests

KB_DEFAULT = "/home/ubuntu/.openclaw/kb"
INDEX_REL = "20_Inbox/urls/index.jsonl"


def utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def slugify(s: str, max_len: int = 80) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff\-_.]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-._")
    return (s[:max_len] or "item")


def normalize_url(url: str) -> str:
    url = url.strip()
    url = url.replace("http://", "https://")
    # canonicalize twitter->x
    url = url.replace("https://twitter.com/", "https://x.com/")
    return url


def host_of(url: str) -> str:
    m = re.match(r"https?://([^/]+)/", url + "/")
    return (m.group(1).lower() if m else "")


def index_path(kb_root: str) -> str:
    return os.path.join(kb_root, INDEX_REL)


def index_has_key(idx_path: str, key: str) -> bool:
    if not os.path.exists(idx_path):
        return False
    try:
        with open(idx_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                    if obj.get("key") == key:
                        return True
                except Exception:
                    continue
    except Exception:
        return False
    return False


def fetch_r_jina(url: str, timeout: int = 40) -> str:
    # r.jina.ai returns a plain-text extracted representation.
    rurl = "https://r.jina.ai/" + url
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(rurl, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text


def parse_jina_text(text: str) -> Tuple[Optional[str], str]:
    # Returns (title, bodyMarkdownOrText)
    title = None
    m = re.search(r"^Title:\s*(.*)$", text, flags=re.M)
    if m:
        title = m.group(1).strip()

    m2 = re.search(r"Markdown Content:\n(.*)\n<<<END_EXTERNAL_UNTRUSTED_CONTENT>>>", text, flags=re.S)
    if m2:
        body = m2.group(1).strip()
        return title, body

    # Fallback: keep full text
    return title, text.strip()


def infer_tags(url: str, title: str, body: str, base: List[str]) -> List[str]:
    # richer rule-based tagger
    from tagger import infer_tags_from_text

    text = f"{title}\n{body}\n{url}"
    return infer_tags_from_text(text, base_tags=base)


def write_kb_entry(
    kb_root: str,
    source: str,
    url: str,
    title: str,
    body_md: str,
    tags: List[str],
    status: str,
    extractor: str,
    note: Optional[str] = None,
) -> str:
    now = utc_now_iso()
    month = now[:7]
    key = sha16(url)

    dir_name = slugify(f"{source}-{key}-{title}".strip(), 80)
    entry_dir = os.path.join(kb_root, "20_Inbox", "urls", month, dir_name)
    ensure_dir(entry_dir)

    header = [
        f"# {title}",
        "",
        f"- Source: {source}",
        f"- URL: {url}",
        f"- IngestedAt: {now}",
        f"- Tags: {' '.join(tags)}",
        f"- Status: {status}",
        "",
    ]
    if note:
        header += ["## 备注", "", note.strip(), ""]

    content = "\n".join(header) + "\n## 内容\n\n" + (body_md.strip() or "(empty)") + "\n"

    meta = {
        "key": key,
        "url": url,
        "title": title,
        "source": source,
        "createdAt": now,
        "tags": tags,
        "status": status,
        "extractor": extractor,
    }
    if note:
        meta["note"] = note

    with open(os.path.join(entry_dir, "content.md"), "w", encoding="utf-8") as f:
        f.write(content)
    with open(os.path.join(entry_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    idx_path = index_path(kb_root)
    ensure_dir(os.path.dirname(idx_path))
    rec = {
        "key": key,
        "path": entry_dir,
        "url": url,
        "title": title,
        "createdAt": now,
        "tags": tags,
        "status": status,
        "source": source,
    }
    with open(idx_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return entry_dir


def ingest(url: str, kb_root: str, extra_tags: List[str], note: Optional[str]) -> Tuple[str, str]:
    url = normalize_url(url)
    host = host_of(url)
    key = sha16(url)

    idx = index_path(kb_root)
    if index_has_key(idx, key):
        return "SKIP", f"Already ingested (key={key})"

    if host in ("x.com", "www.x.com"):
        source = "x"
        base_tags = ["#source:x", "#type:tweet"]
        text = fetch_r_jina(url)
        title, body = parse_jina_text(text)
        title = title or "X post"
        tags = infer_tags(url, title, body, base_tags + extra_tags)
        out_dir = write_kb_entry(kb_root, source, url, title, body, tags, "ok", "r.jina.ai", note)
        return "OK", out_dir

    if host == "mp.weixin.qq.com":
        source = "wechat"
        base_tags = ["#source:wechat", "#type:article"]
        # Try r.jina.ai; if blocked, create placeholder.
        try:
            text = fetch_r_jina(url)
            if "环境异常" in text or "完成验证" in text:
                raise RuntimeError("wechat verification page")
            title, body = parse_jina_text(text)
            title = title or "WeChat article"
            tags = infer_tags(url, title, body, base_tags + extra_tags)
            out_dir = write_kb_entry(kb_root, source, url, title, body, tags, "ok", "r.jina.ai", note)
            return "OK", out_dir
        except Exception:
            title = "WeChat article (blocked)"
            body = "自动抓取失败：公众号页面需要验证。\n\n兜底：请提供截图或复制全文；或稍后通过本地浏览器 relay 抓取。"
            tags = base_tags + ["#needs-manual"] + extra_tags
            out_dir = write_kb_entry(kb_root, source, url, title, body, tags, "blocked_verification", "placeholder", note)
            return "BLOCKED", out_dir

    # generic web
    source = "web"
    base_tags = ["#source:web", "#type:page"]
    text = fetch_r_jina(url)
    title, body = parse_jina_text(text)
    title = title or "Web page"
    tags = infer_tags(url, title, body, base_tags + extra_tags)
    out_dir = write_kb_entry(kb_root, source, url, title, body, tags, "ok", "r.jina.ai", note)
    return "OK", out_dir


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--tags", default="", help='Extra tags, e.g. "#product #reading"')
    ap.add_argument("--note", default="", help="Optional note/context from you")
    args = ap.parse_args(argv[1:])

    kb_root = os.environ.get("KB_ROOT", KB_DEFAULT)
    extra_tags = [t for t in args.tags.split() if t.strip().startswith("#")]
    note = args.note.strip() or None

    status, msg = ingest(args.url, kb_root, extra_tags, note)
    print(status, msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
