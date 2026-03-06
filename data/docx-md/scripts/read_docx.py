#!/usr/bin/env python3
"""
Read .docx and output structured content for AI consumption.
Supports JSON (full structure) and Markdown (compact, token-efficient).
Body only (no headers/footers). Requires: pip install lxml
"""
from __future__ import annotations

import argparse
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def _local(el) -> str:
    return el.tag.split("}")[-1] if "}" in str(el.tag) else el.tag


def _text(el) -> str:
    if el is None:
        return ""
    return "".join(el.itertext()) if hasattr(el, "itertext") else (el.text or "") + "".join((e.tail or "") for e in el.iter())


def _attr(el, name: str, default: str = "") -> str:
    if el is None:
        return default
    for k, v in (el.attrib if hasattr(el, "attrib") else {}).items():
        if k.endswith("}" + name) or k == name:
            return v or default
    return default


def _is_heading(p_el) -> tuple[bool, int]:
    pPr = p_el.find(_tag("pPr"))
    if pPr is None:
        return False, 0
    outline = pPr.find(_tag("outlineLvl"))
    if outline is not None:
        val = _attr(outline, "val", "0")
        try:
            level = int(val) + 1
            if 1 <= level <= 9:
                return True, level
        except ValueError:
            pass
    style = pPr.find(_tag("pStyle"))
    if style is None:
        return False, 0
    val = _attr(style, "val", "")
    if val in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
        return True, int(val)
    if "eading" in val or "Title" in val:
        level = 1
        if "2" in val:
            level = 2
        elif "3" in val:
            level = 3
        return True, level
    return False, 0


def _block_segments(
    el: "etree._Element",
    row_index: int | None = None,
    cell_index: int | None = None,
) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    cell_pos = row_index is not None and cell_index is not None

    def add(s: dict[str, Any]) -> None:
        if cell_pos:
            s = {**s, "rowIndex": row_index, "cellIndex": cell_index}
        segments.append(s)

    def walk(e):
        tag = _local(e)
        if tag == "commentRangeStart":
            cid = _attr(e, "id")
            if cid:
                add({"type": "comment", "id": cid})
            return
        if tag == "ins":
            t = _text(e).strip()
            if t:
                add({"type": "insert", "text": t, "author": _attr(e, "author"), "date": _attr(e, "date")})
            return
        if tag == "del":
            t = _text(e).strip()
            if t:
                add({"type": "delete", "text": t, "author": _attr(e, "author"), "date": _attr(e, "date")})
            return
        if tag == "t":
            if (e.text or "").strip():
                add({"type": "text", "value": (e.text or "").strip()})
            if (e.tail or "").strip():
                add({"type": "text", "value": (e.tail or "").strip()})
            return
        for c in e:
            walk(c)
        if getattr(e, "tail", None) and (e.tail or "").strip():
            add({"type": "text", "value": (e.tail or "").strip()})

    walk(el)
    return segments


def _parse_date(s: str | None) -> datetime | None:
    if not s or not s.strip():
        return None
    s = s.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _same_author_and_near_time(
    author1: str | None, date1: str | None,
    author2: str | None, date2: str | None,
    max_seconds: int = 60,
) -> bool:
    if author1 != author2:
        return False
    if date1 == date2:
        return True
    t1, t2 = _parse_date(date1), _parse_date(date2)
    if t1 is None or t2 is None:
        return date1 == date2
    return abs((t1 - t2).total_seconds()) <= max_seconds


def _merge_segments(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not segments:
        return []
    result: list[dict[str, Any]] = []
    for s in segments:
        if not result:
            result.append(dict(s))
            continue
        prev = result[-1]
        if prev.get("type") != s.get("type"):
            result.append(dict(s))
            continue
        if prev.get("rowIndex") != s.get("rowIndex") or prev.get("cellIndex") != s.get("cellIndex"):
            result.append(dict(s))
            continue
        t = prev["type"]
        if t == "text":
            prev["value"] = prev.get("value", "") + s.get("value", "")
        elif t == "insert":
            if _same_author_and_near_time(prev.get("author"), prev.get("date"), s.get("author"), s.get("date")):
                prev["text"] = prev.get("text", "") + s.get("text", "")
            else:
                result.append(dict(s))
        elif t == "delete":
            if _same_author_and_near_time(prev.get("author"), prev.get("date"), s.get("author"), s.get("date")):
                prev["text"] = prev.get("text", "") + s.get("text", "")
            else:
                result.append(dict(s))
    return result


def _paragraph_block(p_el) -> dict[str, Any]:
    is_h, level = _is_heading(p_el)
    segments = _merge_segments(_block_segments(p_el))
    block_type = f"title{level}" if (is_h and 1 <= level <= 9) else "paragraph"
    out: dict[str, Any] = {"type": block_type, "segments": segments}
    if is_h:
        out["level"] = level
    return out


def _table_block(tbl_el) -> dict[str, Any]:
    segments: list[dict[str, Any]] = []
    for row_idx, tr in enumerate(tbl_el.findall(_tag("tr"))):
        for cell_idx, tc in enumerate(tr.findall(_tag("tc"))):
            segments.extend(_block_segments(tc, row_index=row_idx, cell_index=cell_idx))
    return {"type": "table", "segments": _merge_segments(segments)}


def _parse_comments(zipf: zipfile.ZipFile) -> list[dict[str, Any]]:
    try:
        data = zipf.read("word/comments.xml")
    except KeyError:
        return []
    root = etree.fromstring(data)
    out = []
    for c in root.findall(f".//{{{W_NS}}}comment"):
        out.append({
            "id": _attr(c, "id"),
            "author": _attr(c, "author"),
            "date": _attr(c, "date"),
            "text": _text(c).strip(),
        })
    return out


def read_docx(path: str | Path) -> dict[str, Any]:
    """Read docx and return standard structure: { body, comments, path }. Body blocks have type, segments, blockIndex."""
    path = Path(path)
    if not path.exists():
        return {"error": f"File not found: {path}"}
    try:
        with zipfile.ZipFile(path, "r") as z:
            doc = z.read("word/document.xml")
            comments = _parse_comments(z)
    except Exception as e:
        return {"error": str(e)}

    root = etree.fromstring(doc)
    body = root.find(f".//{{{W_NS}}}body")
    if body is None:
        return {"body": [], "comments": comments, "path": str(path.resolve())}

    blocks: list[dict[str, Any]] = []
    for child in body:
        tag = _local(child)
        if tag == "p":
            blocks.append(_paragraph_block(child))
        elif tag == "tbl":
            blocks.append(_table_block(child))

    for i, b in enumerate(blocks):
        b["blockIndex"] = i

    return {"body": blocks, "comments": comments, "path": str(path.resolve())}


def _segments_to_md_text(segments: list[dict[str, Any]], comments_by_id: dict[str, str]) -> str:
    """Render segments to compact inline text with {+ins+} {-del-} [comment:text] markers."""
    parts: list[str] = []
    for s in segments:
        t = s.get("type")
        if t == "text":
            parts.append(s.get("value", ""))
        elif t == "insert":
            parts.append("{+" + s.get("text", "") + "+}")
        elif t == "delete":
            parts.append("{-" + s.get("text", "") + "-}")
        elif t == "comment":
            cid = s.get("id", "")
            txt = comments_by_id.get(cid, "")
            parts.append("[comment:" + (txt or cid) + "]")
    return "".join(parts)


def _blocks_to_md(data: dict[str, Any]) -> str:
    """Convert body + comments to compact Markdown with blockIndex markers. Saves tokens vs JSON."""
    body = data.get("body", [])
    comments = data.get("comments", [])
    comments_by_id = {str(c.get("id", "")): c.get("text", "") for c in comments}

    lines: list[str] = []
    for b in body:
        idx = b.get("blockIndex", 0)
        block_type = b.get("type", "paragraph")
        segments = b.get("segments", [])

        prefix = f"<!-- b:{idx} -->"
        if block_type.startswith("title"):
            level = b.get("level", 1)
            hashes = "#" * min(level, 6)
            text = _segments_to_md_text(segments, comments_by_id).strip()
            lines.append(f"{prefix}{hashes} {text}")
        elif block_type == "table":
            cells: dict[tuple[int, int], list[dict]] = {}
            for s in segments:
                ri = s.get("rowIndex", 0)
                ci = s.get("cellIndex", 0)
                key = (ri, ci)
                if key not in cells:
                    cells[key] = []
                cells[key].append(s)
            if cells:
                max_row = max(k[0] for k in cells)
                max_col = max(k[1] for k in cells)
                for r in range(max_row + 1):
                    row_cells = [
                        _segments_to_md_text(cells.get((r, c), []), comments_by_id).strip()
                        for c in range(max_col + 1)
                    ]
                    lines.append(f"{prefix}| " + " | ".join(row_cells) + " |")
        else:
            text = _segments_to_md_text(segments, comments_by_id)
            lines.append(f"{prefix}{text}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(
        description="Read docx and output JSON or compact Markdown (default: md for token efficiency)"
    )
    ap.add_argument("docx", help="Path to .docx")
    ap.add_argument("-o", "--output", help="Output path (default: stdout)")
    ap.add_argument(
        "-f", "--format",
        choices=["json", "md"],
        default="md",
        help="Output format: md (compact, token-efficient) or json (full structure). Default: md",
    )
    args = ap.parse_args()
    out = read_docx(args.docx)
    if "error" in out:
        print(json.dumps(out, ensure_ascii=False), file=__import__("sys").stderr)
        __import__("sys").exit(1)

    if args.format == "json":
        s = json.dumps(out, ensure_ascii=False, indent=2)
    else:
        s = _blocks_to_md(out)

    if args.output:
        Path(args.output).write_text(s, encoding="utf-8")
    else:
        print(s)


if __name__ == "__main__":
    main()
