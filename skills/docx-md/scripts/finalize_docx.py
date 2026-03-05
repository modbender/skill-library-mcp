#!/usr/bin/env python3
"""
Finalize .docx: accept all revisions, then remove all comments.
Step 1 — accept revisions: use docx-revisions (python-docx) to avoid XML re-serialization issues.
Step 2 — remove comments: use regex on raw document.xml bytes, no XML parse/serialize.
Requires: pip install docx-revisions
"""
from __future__ import annotations

import argparse
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from io import BytesIO

from docx_revisions import RevisionDocument

# Regex patterns for comment markup only (operate on UTF-8 string)
_RE_COMMENT = re.compile(
    r"<w:(?:commentRangeStart|commentRangeEnd|commentReference)\b[^>]*/>"
)


_RE_RELS_COMMENT = re.compile(r'<Relationship\b[^>]*comments[^>]*/>', re.IGNORECASE)
_RE_CT_COMMENT = re.compile(r'<Override\b[^>]*/word/comments[^>]*/>', re.IGNORECASE)


def _remove_comments_raw(zip_bytes: bytes) -> bytes:
    """Remove comment markup from document.xml using regex; no XML parse."""
    out = BytesIO()
    with zipfile.ZipFile(BytesIO(zip_bytes), "r") as z_in:
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z_out:
            for info in z_in.infolist():
                name = info.filename
                if name == "word/comments.xml":
                    continue
                if name == "word/document.xml":
                    text = z_in.read(name).decode("utf-8")
                    text = _RE_COMMENT.sub("", text)
                    z_out.writestr(info, text.encode("utf-8"))
                elif name == "word/_rels/document.xml.rels":
                    text = z_in.read(name).decode("utf-8")
                    text = _RE_RELS_COMMENT.sub("", text)
                    z_out.writestr(info, text.encode("utf-8"))
                elif name == "[Content_Types].xml":
                    text = z_in.read(name).decode("utf-8")
                    text = _RE_CT_COMMENT.sub("", text)
                    z_out.writestr(info, text.encode("utf-8"))
                else:
                    z_out.writestr(info, z_in.read(name))
    return out.getvalue()


def finalize_docx(src_path: Path, out_path: Path) -> None:
    src_path = Path(src_path)
    out_path = Path(out_path)

    # Step 1: accept all revisions via docx-revisions (preserves encoding)
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        rdoc = RevisionDocument(str(src_path))
        rdoc.accept_all()
        rdoc.document.save(str(tmp_path))

        # Step 2: remove comment markup via regex on raw bytes
        cleaned = _remove_comments_raw(tmp_path.read_bytes())
        out_path.write_bytes(cleaned)
    finally:
        tmp_path.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser(description="Finalize docx: accept all revisions, remove all comments")
    ap.add_argument("docx", help="Input .docx path")
    ap.add_argument("-o", "--output", required=True, help="Output .docx path")
    args = ap.parse_args()
    finalize_docx(args.docx, args.output)
    print(f"Written {args.output}")


if __name__ == "__main__":
    main()
