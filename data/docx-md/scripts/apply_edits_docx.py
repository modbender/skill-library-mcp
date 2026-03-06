#!/usr/bin/env python3
"""
Apply structured edits to a .docx (revision function).
Input: docx path + standard edit JSON (array of edits).
Output: new .docx with proper OOXML tracked changes and inline diff comments.

Diff strategy (op="replace"):
  - Run difflib.SequenceMatcher on characters between original paragraph text
    and new text.
  - Emit inline runs:  plain w:r (equal) / w:del (delete) / w:ins (insert)
  - Minimal change: only touched segments get tracked-change markup.
  - basis → Word comment anchored to the paragraph.

Requires: pip install lxml
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import zipfile
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree  # type: ignore

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def _local(el) -> str:
    return el.tag.split("}")[-1] if "}" in str(el.tag) else el.tag


def _body_blocks(body_el) -> list[tuple[Any, str]]:
    blocks = []
    for child in body_el:
        tag = _local(child)
        if tag == "p":
            blocks.append((child, "p"))
        elif tag == "tbl":
            blocks.append((child, "tbl"))
    return blocks


def _next_revision_id(root_el) -> int:
    max_id = 0
    for el in root_el.iter():
        if _local(el) in ("ins", "del"):
            vid = el.get(_tag("id")) or el.get("id")
            if vid:
                try:
                    max_id = max(max_id, int(vid))
                except ValueError:
                    pass
    return max_id + 1


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Paragraph scanning
# ---------------------------------------------------------------------------

def _scan_paragraph(p_el) -> tuple[str, Any]:
    """
    Read paragraph without modifying it.
    Returns (full_plain_text, deepcopy_of_first_rPr_or_None).
    Handles plain runs, existing w:ins, w:del.
    """
    text_parts: list[str] = []
    rep_rPr = None

    for child in p_el:
        local = _local(child)
        if local in ("pPr", "commentRangeStart", "commentRangeEnd",
                     "bookmarkStart", "bookmarkEnd"):
            continue
        if local == "r":
            for sub in child:
                sl = _local(sub)
                if sl == "rPr" and rep_rPr is None:
                    rep_rPr = copy.deepcopy(sub)
                elif sl == "t":
                    text_parts.append(sub.text or "")
        elif local == "ins":
            for r in child:
                if _local(r) == "r":
                    for sub in r:
                        sl = _local(sub)
                        if sl == "rPr" and rep_rPr is None:
                            rep_rPr = copy.deepcopy(sub)
                        elif sl == "t":
                            text_parts.append(sub.text or "")
        elif local == "del":
            for r in child:
                if _local(r) == "r":
                    for sub in r:
                        sl = _local(sub)
                        if sl == "rPr" and rep_rPr is None:
                            rep_rPr = copy.deepcopy(sub)
                        elif sl == "delText":
                            text_parts.append(sub.text or "")

    return "".join(text_parts), rep_rPr


def _clear_paragraph_content(p_el):
    """Remove all children except pPr; return the pPr element (or None)."""
    pPr = None
    for child in p_el:
        if _local(child) == "pPr":
            pPr = child
    for child in list(p_el):
        p_el.remove(child)
    if pPr is not None:
        p_el.insert(0, pPr)
    return pPr


# ---------------------------------------------------------------------------
# Run builders (inline helpers)
# ---------------------------------------------------------------------------

def _make_plain_run(text: str, rPr) -> Any:
    r = etree.Element(_tag("r"))
    if rPr is not None:
        r.append(copy.deepcopy(rPr))
    t = etree.SubElement(r, _tag("t"))
    t.set(XML_SPACE, "preserve")
    t.text = text
    return r


def _make_del_run(text: str, rPr, rev_id: int, author: str, date: str) -> tuple[Any, int]:
    del_el = etree.Element(_tag("del"), attrib={
        _tag("id"): str(rev_id),
        _tag("author"): author,
        _tag("date"): date,
    })
    del_r = etree.SubElement(del_el, _tag("r"))
    if rPr is not None:
        del_r.append(copy.deepcopy(rPr))
    del_t = etree.SubElement(del_r, _tag("delText"))
    del_t.set(XML_SPACE, "preserve")
    del_t.text = text
    return del_el, rev_id + 1


def _make_ins_run(text: str, rPr, rev_id: int, author: str, date: str) -> tuple[Any, int]:
    ins_el = etree.Element(_tag("ins"), attrib={
        _tag("id"): str(rev_id),
        _tag("author"): author,
        _tag("date"): date,
    })
    ins_r = etree.SubElement(ins_el, _tag("r"))
    if rPr is not None:
        ins_r.append(copy.deepcopy(rPr))
    ins_t = etree.SubElement(ins_r, _tag("t"))
    ins_t.set(XML_SPACE, "preserve")
    ins_t.text = text
    return ins_el, rev_id + 1


def _get_paragraph_properties(p_el) -> Any:
    """Get pPr (paragraph properties) from a paragraph element, or None."""
    for child in p_el:
        if _local(child) == "pPr":
            return copy.deepcopy(child)
    return None


def _insert_paragraph_after(ref_p_el, content: str, author: str, date: str, rev_id: int,
                            comment_text: str, comments_root, comments_bytes,
                            next_cid: int) -> tuple[Any, Any, int, int]:
    """
    Insert a new paragraph after ref_p_el. New paragraph format matches ref (pPr, rPr).
    Entire content is wrapped in w:ins (tracked insertion).
    Returns (comments_root, comments_bytes, new_rev_id, new_next_cid).
    """
    _, rep_rPr = _scan_paragraph(ref_p_el)
    pPr = _get_paragraph_properties(ref_p_el)

    new_p = etree.Element(_tag("p"))
    if pPr is not None:
        new_p.append(pPr)

    ins_node, rev_id = _make_ins_run(content, rep_rPr, rev_id, author, date)
    new_p.append(ins_node)

    parent = ref_p_el.getparent()
    idx = list(parent).index(ref_p_el)
    parent.insert(idx + 1, new_p)

    if comment_text:
        comments_root, comments_bytes = _ensure_comments_root(comments_root, comments_bytes)
        _add_comment_to_paragraph(new_p, str(next_cid), author, date,
                                  comment_text, comments_root)
        next_cid += 1

    return comments_root, comments_bytes, rev_id, next_cid


# ---------------------------------------------------------------------------
# Core tracked-change functions
# ---------------------------------------------------------------------------

def _build_diff_runs(orig: str, new: str, rep_rPr, rev_id: int, author: str, date: str
                     ) -> tuple[list, int]:
    """
    Build run elements from diff(orig, new). Returns (list of elements, updated rev_id).
    """
    result = []
    matcher = SequenceMatcher(None, orig, new, autojunk=False)
    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode == "equal":
            seg = orig[i1:i2]
            if seg:
                result.append(_make_plain_run(seg, rep_rPr))
        elif opcode == "delete":
            seg = orig[i1:i2]
            if seg:
                node, rev_id = _make_del_run(seg, rep_rPr, rev_id, author, date)
                result.append(node)
        elif opcode == "insert":
            seg = new[j1:j2]
            if seg:
                node, rev_id = _make_ins_run(seg, rep_rPr, rev_id, author, date)
                result.append(node)
        elif opcode == "replace":
            old_seg, new_seg = orig[i1:i2], new[j1:j2]
            if old_seg:
                node, rev_id = _make_del_run(old_seg, rep_rPr, rev_id, author, date)
                result.append(node)
            if new_seg:
                node, rev_id = _make_ins_run(new_seg, rep_rPr, rev_id, author, date)
                result.append(node)
    return result, rev_id


def _replace_paragraph_tracked(p_el, new_text: str | None, author: str, date: str, rev_id: int,
                               original_content: str | None = None) -> int:
    """
    Apply tracked changes using originalContent vs content (段内替换).

    Strategy:
      - Prefer diff(original_content, new_text) when original_content is provided and
        found in the paragraph → 段内替换 (segment replace).
      - Fallback: diff(docx_paragraph_text, new_text) when original_content is empty,
        not found, or not provided.

    Cases:
      new_text non-empty  →  inline diff with equal/del/ins
      new_text None/empty →  mark entire paragraph as w:del (delete-only)

    Preserves pPr and rPr. Returns updated rev_id.
    """
    orig_text, rep_rPr = _scan_paragraph(p_el)
    _clear_paragraph_content(p_el)

    if new_text:
        # ── 段内替换：优先用 original_content 与 content 做 diff ─────
        orig_for_diff = orig_text
        before, after = "", ""

        if original_content and original_content.strip():
            oc = original_content.strip()
            pos = orig_text.find(oc)
            if pos >= 0:
                before = orig_text[:pos]
                after = orig_text[pos + len(oc):]
                orig_for_diff = oc

        # diff(orig_for_diff, new_text) 生成 runs
        runs, rev_id = _build_diff_runs(
            orig_for_diff, new_text, rep_rPr, rev_id, author, date
        )
        # 插入 before + 段内 runs + after
        if before:
            p_el.append(_make_plain_run(before, rep_rPr))
        for r in runs:
            p_el.append(r)
        if after:
            p_el.append(_make_plain_run(after, rep_rPr))

    else:
        # ── Delete-only mode ───────────────────────────────────────────────
        if orig_text:
            node, rev_id = _make_del_run(orig_text, rep_rPr, rev_id, author, date)
            p_el.append(node)

    return rev_id


def _flatten_paragraph_content(p_el) -> list:
    """Accept ins, drop del, skip comment nodes — for accept_revision."""
    parts = []

    def walk(e):
        tag = _local(e)
        if tag in ("commentRangeStart", "commentRangeEnd", "commentReference"):
            return
        if tag == "ins":
            parts.append(("text", "".join(e.itertext()).strip()))
            return
        if tag == "del":
            return
        if tag == "t":
            if (e.text or "").strip():
                parts.append(("text", (e.text or "").strip()))
            return
        for c in e:
            walk(c)

    for c in p_el:
        walk(c)
    return parts


def _accept_revision_paragraph(p_el) -> None:
    parts = _flatten_paragraph_content(p_el)
    final_text = "".join(t for _, t in parts)
    pPr = None
    for child in list(p_el):
        if _local(child) == "pPr":
            pPr = child
        p_el.remove(child)
    if pPr is not None:
        p_el.insert(0, pPr)
    if final_text:
        r = etree.SubElement(p_el, _tag("r"))
        t = etree.SubElement(r, _tag("t"))
        t.text = final_text


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def _max_comment_id(comments_root) -> int:
    m = 0
    for c in comments_root.findall(f".//{{{W_NS}}}comment"):
        vid = c.get(_tag("id")) or c.get("id")
        if vid:
            try:
                m = max(m, int(vid))
            except ValueError:
                pass
    return m


def _add_comment_to_paragraph(p_el, comment_id: str, comment_author: str,
                               comment_date: str, comment_text: str, comments_root) -> None:
    """Anchor a Word comment to the whole paragraph."""
    comm = etree.SubElement(comments_root, _tag("comment"), attrib={
        _tag("id"): comment_id,
        _tag("author"): comment_author,
        _tag("date"): comment_date,
    })
    cp = etree.SubElement(comm, _tag("p"))
    cr = etree.SubElement(cp, _tag("r"))
    ct = etree.SubElement(cr, _tag("t"))
    ct.set(XML_SPACE, "preserve")
    ct.text = comment_text or ""

    start_anchor = etree.Element(_tag("commentRangeStart"), attrib={_tag("id"): comment_id})
    end_anchor = etree.Element(_tag("commentRangeEnd"), attrib={_tag("id"): comment_id})
    ref_r = etree.Element(_tag("r"))
    etree.SubElement(ref_r, _tag("commentReference"), attrib={_tag("id"): comment_id})

    p_el.insert(0, start_anchor)
    p_el.append(end_anchor)
    p_el.append(ref_r)


def _ensure_comments_root(comments_root, comments_bytes):
    if comments_root is None:
        comments_root = etree.Element(f"{{{W_NS}}}comments", nsmap={"w": W_NS})
        comments_bytes = None
    return comments_root, comments_bytes


# ---------------------------------------------------------------------------
# Main apply function
# ---------------------------------------------------------------------------

def apply_edits_docx(docx_path: Path, edits: list[dict[str, Any]],
                     out_path: Path, author: str = "Review",
                     date: str | None = None) -> None:
    date = date or _iso_now()
    docx_path = Path(docx_path)
    out_path = Path(out_path)

    with zipfile.ZipFile(docx_path, "r") as z_in:
        doc_bytes = z_in.read("word/document.xml")
        try:
            comments_bytes = z_in.read("word/comments.xml")
            comments_root = etree.fromstring(comments_bytes)
        except KeyError:
            comments_root = None
            comments_bytes = None

    doc_root = etree.fromstring(doc_bytes)
    body = doc_root.find(f".//{{{W_NS}}}body")
    if body is None:
        raise ValueError("No w:body in document.xml")

    blocks = _body_blocks(body)
    rev_id = _next_revision_id(doc_root)
    next_cid = _max_comment_id(comments_root) + 1 if comments_root is not None else 0

    regular_edits = [e for e in edits if e.get("op") != "insert_paragraph_after"]
    insert_edits = [e for e in edits if e.get("op") == "insert_paragraph_after"]

    for edit in regular_edits:
        op = edit.get("op")
        block_index = edit.get("blockIndex", -1)
        if block_index < 0 or block_index >= len(blocks):
            continue
        el, kind = blocks[block_index]
        if kind != "p":
            continue

        edit_author = edit.get("author", author)
        edit_date = edit.get("date", date)
        comment_text = edit.get("comment_text", "")

        if op == "replace":
            rev_id = _replace_paragraph_tracked(
                el, edit.get("text") or "", edit_author, edit_date, rev_id,
                original_content=edit.get("original_content") or edit.get("originalContent"),
            )
            if comment_text:
                comments_root, comments_bytes = _ensure_comments_root(comments_root, comments_bytes)
                _add_comment_to_paragraph(el, str(next_cid), edit_author, edit_date,
                                          comment_text, comments_root)
                next_cid += 1

        elif op == "delete":
            rev_id = _replace_paragraph_tracked(
                el, None, edit_author, edit_date, rev_id
            )
            if comment_text:
                comments_root, comments_bytes = _ensure_comments_root(comments_root, comments_bytes)
                _add_comment_to_paragraph(el, str(next_cid), edit_author, edit_date,
                                          comment_text, comments_root)
                next_cid += 1

        elif op in ("add_comment", "comment"):
            text = comment_text or edit.get("text", "")
            if text:
                comments_root, comments_bytes = _ensure_comments_root(comments_root, comments_bytes)
                _add_comment_to_paragraph(el, str(next_cid), edit_author, edit_date,
                                          text, comments_root)
                next_cid += 1

        elif op == "accept_revision":
            _accept_revision_paragraph(el)

    for edit in insert_edits:
        block_index = edit.get("blockIndex", -1)
        if block_index < 0 or block_index >= len(blocks):
            continue
        el, kind = blocks[block_index]
        if kind != "p":
            continue
        edit_author = edit.get("author", author)
        edit_date = edit.get("date", date)
        comment_text = edit.get("comment_text", "")
        comments_root, comments_bytes, rev_id, next_cid = _insert_paragraph_after(
            el, edit.get("text") or "", edit_author, edit_date, rev_id,
            comment_text, comments_root, comments_bytes, next_cid
        )

    # Serialize
    doc_xml = etree.tostring(doc_root, encoding="utf-8", xml_declaration=True, standalone=True)
    comments_xml = (
        etree.tostring(comments_root, encoding="utf-8", xml_declaration=True, standalone=True)
        if comments_root is not None else None
    )

    orig_names = set(zipfile.ZipFile(docx_path, "r").namelist())

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z_out:
        with zipfile.ZipFile(docx_path, "r") as z_in:
            for name in z_in.namelist():
                if name == "word/document.xml":
                    z_out.writestr(name, doc_xml)
                elif name == "word/comments.xml":
                    z_out.writestr(name, comments_xml if comments_xml is not None else z_in.read(name))
                elif name == "word/_rels/document.xml.rels" and comments_bytes is None and comments_xml is not None:
                    rels = z_in.read(name).decode("utf-8")
                    if "comments.xml" not in rels:
                        rels = rels.replace(
                            "</Relationships>",
                            '\r\n  <Relationship Id="rIdComments"'
                            ' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"'
                            ' Target="comments.xml"/></Relationships>',
                        )
                    z_out.writestr(name, rels)
                elif name == "[Content_Types].xml" and comments_bytes is None and comments_xml is not None:
                    ct = z_in.read(name).decode("utf-8")
                    if "comments" not in ct.lower():
                        ct = ct.replace(
                            "</Types>",
                            '  <Override PartName="/word/comments.xml"'
                            ' ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>\n</Types>',
                        )
                    z_out.writestr(name, ct)
                else:
                    z_out.writestr(name, z_in.read(name))

    if comments_xml is not None and "word/comments.xml" not in orig_names:
        with zipfile.ZipFile(out_path, "a", zipfile.ZIP_DEFLATED) as z_out:
            z_out.writestr("word/comments.xml", comments_xml)


# ---------------------------------------------------------------------------
# Edit normalizer
# ---------------------------------------------------------------------------

def _normalize_edits(raw: Any) -> list[dict[str, Any]]:
    """
    Parse edits.json (4-field format) into internal op-list.

    AI only outputs: blockIndex, originalContent, content, basis.
    Script infers op from fields (no op field required):

    Field semantics:
      blockIndex       — paragraph index (required)
      originalContent  — original text for diff / delete / reference
      content          — new text; empty = delete or pure annotation
      basis            — reason / legal basis → Word comment

    Op inference:
      content non-empty, originalContent non-empty → replace  (diff 段内替换)
      content non-empty, originalContent empty     → insert_paragraph_after (在 block 后新增段落)
      content empty, originalContent non-empty     → delete   (w:del + comment)
      content empty, originalContent empty         → add_comment (pure annotation)
    """
    if isinstance(raw, dict) and "modifications" in raw:
        items = raw["modifications"]
    elif isinstance(raw, list):
        items = raw
    else:
        return []

    result = []
    for item in items:
        if not isinstance(item, dict):
            continue

        block_index = item.get("blockIndex")
        if block_index is None or not isinstance(block_index, int) or block_index < 0:
            continue

        content = (item.get("content") or "").strip()
        original = (item.get("originalContent") or "").strip()
        basis = (item.get("basis") or "").strip()

        if content:
            if original:
                result.append({
                    "op": "replace",
                    "blockIndex": block_index,
                    "text": content,
                    "original_content": original,
                    "comment_text": basis,
                })
            else:
                result.append({
                    "op": "insert_paragraph_after",
                    "blockIndex": block_index,
                    "text": content,
                    "comment_text": basis,
                })
        elif original:
            # content="" but originalContent present → delete
            result.append({
                "op": "delete",
                "blockIndex": block_index,
                "comment_text": basis,
            })
        elif basis:
            # both empty → pure annotation
            result.append({
                "op": "add_comment",
                "blockIndex": block_index,
                "comment_text": basis,
            })

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Apply contract-review edits with inline diff tracked changes and comments"
    )
    ap.add_argument("docx", help="Input .docx path")
    ap.add_argument("edits", help="JSON file with modifications array, or - for stdin")
    ap.add_argument("-o", "--output", required=True, help="Output .docx path")
    ap.add_argument("--author", default="Review", help="Author name for revisions/comments")
    args = ap.parse_args()

    raw = json.load(sys.stdin) if args.edits == "-" else json.loads(Path(args.edits).read_text(encoding="utf-8"))
    edits = _normalize_edits(raw)
    apply_edits_docx(Path(args.docx), edits, Path(args.output), author=args.author)
    print(f"Written {args.output}")


if __name__ == "__main__":
    main()
