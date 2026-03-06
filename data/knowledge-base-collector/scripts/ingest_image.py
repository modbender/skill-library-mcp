#!/usr/bin/env python3
"""KB ingest for screenshots/images (MVP)

This script *stores the image* into the shared KB and writes a content.md/meta.json/index.jsonl.

OCR/vision is intentionally NOT done inside the script (no dependencies). Instead:
- pass extracted text via --text-file (recommended), or
- leave it empty and mark status=needs_ocr.

Usage:
  python3 kb_ingest_image.py /path/to/image.png --text-file /path/to/extracted.txt --tags "#foo #bar" --note "..."

Env:
  KB_ROOT (optional): defaults to /home/ubuntu/.openclaw/kb
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
from typing import List, Optional

KB_DEFAULT = "/home/ubuntu/.openclaw/kb"
INDEX_REL = "20_Inbox/urls/index.jsonl"


def utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha16_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]


def sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def slugify(s: str, max_len: int = 80) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff\-_.]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-._")
    return (s[:max_len] or "image")


def index_path(kb_root: str) -> str:
    return os.path.join(kb_root, INDEX_REL)


def infer_tags(text: str, base: List[str]) -> List[str]:
    from tagger import infer_tags_from_text

    return infer_tags_from_text(text or "", base_tags=base)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image_path")
    ap.add_argument("--text-file", default="")
    ap.add_argument("--title", default="")
    ap.add_argument("--tags", default="", help='Extra tags, e.g. "#product #reading"')
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    kb_root = os.environ.get("KB_ROOT", KB_DEFAULT)
    now = utc_now_iso()
    month = now[:7]

    img_path = os.path.abspath(args.image_path)
    if not os.path.exists(img_path):
        raise SystemExit(f"Image not found: {img_path}")

    with open(img_path, "rb") as f:
        blob = f.read()
    img_key = sha16_bytes(blob)

    extracted_text = ""
    if args.text_file:
        with open(args.text_file, "r", encoding="utf-8") as f:
            extracted_text = f.read().strip()

    title = args.title.strip() or "Screenshot"
    source = "image"

    base_tags = ["#source:image", "#type:screenshot"]
    extra_tags = [t for t in args.tags.split() if t.strip().startswith("#")]
    tags = infer_tags(extracted_text, base_tags + extra_tags)

    status = "ok" if extracted_text else "needs_ocr"
    key = sha16(f"image:{img_key}")

    dir_name = slugify(f"img-{key}-{title}", 80)
    entry_dir = os.path.join(kb_root, "20_Inbox", "urls", month, dir_name)
    ensure_dir(entry_dir)

    # copy image
    ext = os.path.splitext(img_path)[1].lower() or ".img"
    img_out = os.path.join(entry_dir, f"image{ext}")
    shutil.copyfile(img_path, img_out)

    note = args.note.strip() or None

    header = [
        f"# {title}",
        "",
        f"- Source: {source}",
        f"- Image: {os.path.basename(img_out)}",
        f"- IngestedAt: {now}",
        f"- Tags: {' '.join(tags)}",
        f"- Status: {status}",
        "",
    ]
    if note:
        header += ["## 备注", "", note, ""]

    body = extracted_text or "(未做 OCR：请提供 extracted text，或由上层 vision 先抽取再入库)"
    content = "\n".join(header) + "\n## OCR/提取文本\n\n" + body + "\n"

    meta = {
        "key": key,
        "imageKey": img_key,
        "title": title,
        "source": source,
        "createdAt": now,
        "tags": tags,
        "status": status,
        "imageFile": os.path.basename(img_out),
        "extractor": "external-vision" if extracted_text else "placeholder",
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
        "title": title,
        "createdAt": now,
        "tags": tags,
        "status": status,
        "source": source,
    }
    with open(idx_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(entry_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
