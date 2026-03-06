#!/usr/bin/env python3
"""OCR a PDF (or image) with Mistral OCR and write deterministic outputs.

Supports:
- Local PDF path (auto-uploads to Mistral Files API with purpose=ocr)
- Public document URL (document_url)
- Optional document annotation for whole-document structured extraction

Outputs:
- raw_response.json (full OCR response)
- combined.md (all pages concatenated)
- pages/page-XYZ.md (per-page markdown)
- images/ (decoded images when include_image_base64=True)
- tables/ (best-effort extraction when table_format is set)
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# The official SDK uses this import path in Mistral's docs.
try:
    from mistralai import Mistral  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "Missing dependency 'mistralai'. Install it (for example): pip install mistralai\n"
        f"Original import error: {e}"
    )


class CLIError(RuntimeError):
    pass


def _to_plain_dict(obj: Any) -> Any:
    """Convert SDK response objects into JSON-serialisable Python objects."""
    if obj is None:
        return None
    # Pydantic v2 model
    dump = getattr(obj, "model_dump", None)
    if callable(dump):
        return dump()
    # Pydantic v1 model
    dict_fn = getattr(obj, "dict", None)
    if callable(dict_fn):
        return dict_fn()
    if isinstance(obj, dict):
        return {k: _to_plain_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_plain_dict(v) for v in obj]
    # Dataclasses
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _to_plain_dict(getattr(obj, k)) for k in obj.__dataclass_fields__.keys()}
    # Plain objects: best effort
    if hasattr(obj, "__dict__") and not isinstance(obj, (str, int, float, bool)):
        return {k: _to_plain_dict(v) for k, v in vars(obj).items() if not k.startswith("_")}
    return obj


_PAGE_SPEC_RE = re.compile(r"^\s*(\d+)(?:\s*-\s*(\d+))?\s*$")


def parse_pages_spec(spec: Optional[str]) -> Optional[List[int]]:
    """Parse a pages spec like '0,2-4,7' into a sorted unique list of ints."""
    if spec is None or not spec.strip():
        return None
    pages: List[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = _PAGE_SPEC_RE.match(part)
        if not m:
            raise CLIError(f"Invalid --pages segment: {part!r}. Use like 0,2-4,7")
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) is not None else start
        if end < start:
            raise CLIError(f"Invalid --pages range: {part!r} (end < start)")
        pages.extend(range(start, end + 1))
    # de-dup + sort
    return sorted(set(pages))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def decode_maybe_data_uri(b64: str) -> bytes:
    """Decode base64, tolerating optional data URI prefixes."""
    # Common shapes: "data:image/png;base64,AAAA" or raw base64 "AAAA"
    if "," in b64 and b64.lstrip().lower().startswith("data:"):
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64, validate=False)


def safe_write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", errors="replace")


def safe_write_bytes(path: Path, data: bytes) -> None:
    path.write_bytes(data)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="OCR PDFs/images via Mistral OCR and write Markdown/JSON outputs.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", type=str, help="Local file path (PDF or image). Uploaded to Mistral Files API.")
    src.add_argument("--url", type=str, help="Public URL to a PDF or image.")
    p.add_argument("--out", type=str, required=True, help="Output directory.")
    p.add_argument("--model", type=str, default="mistral-ocr-latest", help="OCR model to use.")
    p.add_argument(
        "--table-format",
        choices=["inline", "markdown", "html"],
        default="inline",
        help="Table extraction mode. 'inline' keeps tables in Markdown; others also populate page.tables.",
    )
    p.add_argument("--extract-header", action="store_true", help="Extract header into page.header.")
    p.add_argument("--extract-footer", action="store_true", help="Extract footer into page.footer.")
    p.add_argument(
        "--include-image-base64",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Whether to include base64 image data for extracted figures.",
    )
    p.add_argument("--image-limit", type=int, default=None, help="Max images to extract.")
    p.add_argument("--image-min-size", type=int, default=None, help="Minimum width/height of images to extract.")
    p.add_argument("--pages", type=str, default=None, help="Page selection: '0,2-4,7' (0-indexed).")

    # Document-level structured extraction
    p.add_argument(
        "--annotation-prompt",
        type=str,
        default=None,
        help="Optional prompt to extract structured info from the entire document.",
    )
    p.add_argument(
        "--annotation-format",
        choices=["text", "json_object"],
        default="json_object",
        help="document_annotation_format.type to use when annotation prompt is set.",
    )

    p.add_argument(
        "--cleanup-upload",
        action="store_true",
        help="Attempt to delete the uploaded file after OCR (best effort).",
    )

    return p


@dataclass
class Source:
    kind: str  # 'file_id' | 'document_url'
    payload: Dict[str, Any]
    uploaded_file_id: Optional[str] = None


def require_api_key() -> str:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise CLIError("MISTRAL_API_KEY is not set in the environment")
    return api_key


def is_probably_pdf(path_or_url: str) -> bool:
    return path_or_url.lower().endswith(".pdf")


def prepare_source(client: Mistral, args: argparse.Namespace) -> Source:
    if args.url:
        url = args.url
        # Use document_url for PDFs and image_url for images.
        if is_probably_pdf(url):
            return Source(kind="document_url", payload={"type": "document_url", "document_url": url})
        return Source(kind="image_url", payload={"type": "image_url", "image_url": url})

    in_path = Path(args.input)
    if not in_path.exists() or not in_path.is_file():
        raise CLIError(f"Input file not found: {in_path}")

    # Upload to Files API with purpose='ocr'
    upload = client.files.upload(
        file={"file_name": in_path.name, "content": open(in_path, "rb")},
        purpose="ocr",
    )
    upload_dict = _to_plain_dict(upload)
    file_id = upload_dict.get("id") or upload_dict.get("file_id")
    if not file_id:
        raise CLIError(f"Upload succeeded but no file id returned. Response keys: {list(upload_dict.keys())}")

    return Source(kind="file_id", payload={"file_id": file_id}, uploaded_file_id=file_id)


def call_ocr(client: Mistral, source: Source, args: argparse.Namespace) -> Dict[str, Any]:
    pages = parse_pages_spec(args.pages)

    table_format = None if args.table_format == "inline" else args.table_format

    ocr_kwargs: Dict[str, Any] = {
        "model": args.model,
        "document": source.payload,
        "table_format": table_format,
        "extract_header": bool(args.extract_header),
        "extract_footer": bool(args.extract_footer),
        "include_image_base64": bool(args.include_image_base64),
    }

    if pages is not None:
        ocr_kwargs["pages"] = pages
    if args.image_limit is not None:
        ocr_kwargs["image_limit"] = args.image_limit
    if args.image_min_size is not None:
        ocr_kwargs["image_min_size"] = args.image_min_size

    if args.annotation_prompt:
        ocr_kwargs["document_annotation_prompt"] = args.annotation_prompt
        ocr_kwargs["document_annotation_format"] = {"type": args.annotation_format}

    res = client.ocr.process(**ocr_kwargs)
    return _to_plain_dict(res)


def best_effort_delete_upload(client: Mistral, file_id: str) -> None:
    # Not all SDK versions expose delete; swallow errors.
    try:
        delete = getattr(client.files, "delete", None)
        if callable(delete):
            delete(file_id=file_id)
    except Exception:
        pass


def extract_tables(page: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """Return (suggested_filename, ext, content) for table outputs."""
    out: List[Tuple[str, str, str]] = []
    tables = page.get("tables")
    if not isinstance(tables, list):
        return out

    for i, tbl in enumerate(tables):
        if not isinstance(tbl, dict):
            continue
        tbl_id = str(tbl.get("id") or f"tbl-{i}")

        # Heuristics: common keys seen in OCR outputs.
        html = tbl.get("html") or tbl.get("table_html") or tbl.get("content_html")
        md = tbl.get("markdown") or tbl.get("table_markdown") or tbl.get("content_markdown")

        if isinstance(html, str) and html.strip():
            out.append((tbl_id, "html", html))
        elif isinstance(md, str) and md.strip():
            out.append((tbl_id, "md", md))
        else:
            # Unknown structure; dump JSON for visibility.
            out.append((tbl_id, "json", json.dumps(tbl, ensure_ascii=False, indent=2)))

    return out


def write_outputs(out_dir: Path, ocr: Dict[str, Any]) -> None:
    ensure_dir(out_dir)
    ensure_dir(out_dir / "pages")

    write_json(out_dir / "raw_response.json", ocr)

    pages = ocr.get("pages")
    if not isinstance(pages, list):
        raise CLIError("Unexpected OCR response: missing 'pages' list")

    combined_parts: List[str] = []

    images_dir = out_dir / "images"
    tables_dir = out_dir / "tables"

    for page in pages:
        if not isinstance(page, dict):
            continue
        idx = page.get("index")
        try:
            idx_int = int(idx)
        except Exception:
            idx_int = len(combined_parts)

        md = page.get("markdown") or ""
        if not isinstance(md, str):
            md = str(md)

        page_md_name = f"page-{idx_int:03d}.md"
        safe_write_text(out_dir / "pages" / page_md_name, md)

        combined_parts.append(f"\n\n<!-- page {idx_int} -->\n\n" + md)

        # Images
        images = page.get("images")
        if isinstance(images, list) and images:
            ensure_dir(images_dir)
            for img in images:
                if not isinstance(img, dict):
                    continue
                img_id = img.get("id")
                b64 = img.get("image_base64")
                if not img_id or not isinstance(img_id, str):
                    continue
                if not b64 or not isinstance(b64, str):
                    continue
                try:
                    data = decode_maybe_data_uri(b64)
                except Exception:
                    continue
                safe_write_bytes(images_dir / img_id, data)

        # Tables
        table_blobs = extract_tables(page)
        if table_blobs:
            ensure_dir(tables_dir)
            for tbl_id, ext, content in table_blobs:
                safe_write_text(tables_dir / f"{tbl_id}.{ext}", content)

    safe_write_text(out_dir / "combined.md", "\n\n---\n\n".join(combined_parts).lstrip())

    # Document annotation
    ann = ocr.get("document_annotation")
    if isinstance(ann, str) and ann.strip():
        # Try JSON parse; if it fails, still store raw.
        ann_path_json = out_dir / "document_annotation.json"
        ann_path_txt = out_dir / "document_annotation.txt"
        try:
            parsed = json.loads(ann)
            write_json(ann_path_json, parsed)
        except Exception:
            safe_write_text(ann_path_txt, ann)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        api_key = require_api_key()
        out_dir = Path(args.out)
        ensure_dir(out_dir)

        client = Mistral(api_key=api_key)

        source = prepare_source(client, args)
        ocr = call_ocr(client, source, args)

        write_outputs(out_dir, ocr)

        if args.cleanup_upload and source.uploaded_file_id:
            best_effort_delete_upload(client, source.uploaded_file_id)

        print(str(out_dir.resolve()))
        return 0
    except CLIError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
