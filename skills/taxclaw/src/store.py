from __future__ import annotations

import hashlib
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import fitz

from .config import Config
from .db import db, json_dumps, row_to_dict


ALLOWED_UPLOAD_EXTS = {"pdf", "png", "jpg", "jpeg", "tiff", "webp"}


def sniff_mime_type(path: Path) -> str:
    """Best-effort file type sniffing based on magic bytes.

    We avoid heavy dependencies (e.g., libmagic) and only support the formats
    TaxClaw explicitly allows.
    """

    head = b""
    with open(path, "rb") as f:
        head = f.read(64)

    if head.startswith(b"%PDF-"):
        return "application/pdf"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"II*\x00") or head.startswith(b"MM\x00*"):
        return "image/tiff"
    # WEBP: RIFF....WEBP
    if len(head) >= 12 and head[0:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"

    return "application/octet-stream"


def _dir_size_bytes(p: Path) -> int:
    total = 0
    if not p.exists():
        return 0
    for fp in p.glob("*"):
        try:
            if fp.is_file():
                total += fp.stat().st_size
        except Exception:
            continue
    return total


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ingest_file(src_path: str, cfg: Config, original_name: str | None = None) -> tuple[str, str, str, str]:
    """Copy to data_dir/files/{sha256}.{ext} and return (dest_path, file_hash, original_filename, mime_type).

    Security notes:
    - Enforces max upload size.
    - Enforces extension allowlist.
    - Sniffs magic bytes to confirm declared type.
    - Enforces a coarse total storage cap.
    """

    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(src_path)

    size = src.stat().st_size
    if size > int(cfg.max_upload_bytes):
        raise ValueError(f"file too large ({size} bytes) — max is {int(cfg.max_upload_bytes)}")

    original_filename = original_name or src.name
    safe_original_name = Path(original_filename).name

    # Extension allowlist (from user-visible name when provided)
    ext = Path(safe_original_name).suffix.lower().lstrip(".") or src.suffix.lower().lstrip(".")
    if ext == "jpg":
        ext = "jpeg"

    if ext not in ALLOWED_UPLOAD_EXTS:
        raise ValueError(f"unsupported file type: .{ext}")

    # Magic-byte sniff. We accept JPEG for both jpg/jpeg extension.
    sniffed = sniff_mime_type(src)
    if ext == "pdf" and sniffed != "application/pdf":
        raise ValueError("file extension .pdf does not match detected type")
    if ext in {"jpeg"} and sniffed != "image/jpeg":
        raise ValueError("file extension .jpg/.jpeg does not match detected type")
    if ext == "png" and sniffed != "image/png":
        raise ValueError("file extension .png does not match detected type")
    if ext == "tiff" and sniffed != "image/tiff":
        raise ValueError("file extension .tiff does not match detected type")
    if ext == "webp" and sniffed != "image/webp":
        raise ValueError("file extension .webp does not match detected type")

    file_hash = sha256_file(str(src))

    files_dir = cfg.data_path / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    dest_path = files_dir / f"{file_hash}.{ext}"

    # Storage cap is enforced only when we would create a new stored object.
    if not dest_path.exists():
        used = _dir_size_bytes(files_dir)
        if used + size > int(cfg.storage_cap_bytes):
            raise ValueError(
                f"storage cap exceeded (used {used} bytes, adding {size} bytes, cap {int(cfg.storage_cap_bytes)} bytes)"
            )
        shutil.copy2(str(src), str(dest_path))

    mime_type = sniffed
    return str(dest_path), file_hash, safe_original_name, mime_type


def create_document_record(
    *,
    cfg: Config,
    file_path: str,
    file_hash: str,
    original_filename: str,
    mime_type: str,
    filer: str | None,
    tax_year: int | None,
    doc_type: str,
    page_count: int,
    classification_confidence: float | None,
) -> str:
    doc_id = str(uuid.uuid4())
    with db() as con:
        con.execute(
            """INSERT INTO documents (
                id, file_path, file_hash, original_filename, mime_type,
                tax_year, doc_type, filer,
                page_count, status, classification_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'processing', ?)""",
            (
                doc_id,
                file_path,
                file_hash,
                original_filename,
                mime_type,
                tax_year,
                doc_type,
                filer,
                page_count,
                classification_confidence,
            ),
        )
    return doc_id


def get_document_by_hash(file_hash: str) -> dict[str, Any] | None:
    with db() as con:
        r = con.execute("SELECT * FROM documents WHERE file_hash = ?", (file_hash,)).fetchone()
        return row_to_dict(r)


def get_document(doc_id: str) -> dict[str, Any] | None:
    with db() as con:
        r = con.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        return row_to_dict(r)


def list_documents(
    *,
    filer: str | None = None,
    year: int | None = None,
    doc_type: str | None = None,
    needs_review: int | None = None,
) -> list[dict[str, Any]]:
    q = "SELECT * FROM documents WHERE 1=1"
    params: list[Any] = []
    if filer:
        q += " AND filer = ?"
        params.append(filer)
    if year:
        q += " AND tax_year = ?"
        params.append(year)
    if doc_type:
        q += " AND doc_type = ?"
        params.append(doc_type)
    if needs_review is not None:
        q += " AND needs_review = ?"
        params.append(int(needs_review))
    q += " ORDER BY created_at DESC"
    with db() as con:
        rows = con.execute(q, tuple(params)).fetchall()
        return [row_to_dict(r) for r in rows if r is not None]  # type: ignore


def store_raw_extraction(*, doc_id: str, form_type: str, data: Any, confidence: float | None = None) -> str:
    section_id = str(uuid.uuid4())
    with db() as con:
        con.execute(
            """INSERT INTO form_sections (
                id, document_id, form_type, section_page_start, section_page_end, raw_json, confidence
            ) VALUES (?, ?, ?, NULL, NULL, ?, ?)""",
            (section_id, doc_id, form_type, json_dumps(data), confidence),
        )
        con.execute(
            "INSERT INTO form_extractions (id, document_id, form_type, raw_json, confidence) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), doc_id, form_type, json_dumps(data), confidence),
        )
    return section_id


def _walk_fields(obj: Any, prefix: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}{k}" if not prefix else f"{prefix}.{k}"
            yield from _walk_fields(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{prefix}[{i}]"
            yield from _walk_fields(v, p)
    else:
        yield prefix, obj


def store_extracted_fields(*, doc_id: str, section_id: str | None, data: Any) -> None:
    rows: list[tuple[str, str, str | None]] = []
    for path, value in _walk_fields(data):
        if not path:
            continue
        if value is None:
            v = None
        elif isinstance(value, (str, int, float, bool)):
            v = str(value)
        else:
            v = json_dumps(value)
        rows.append((str(uuid.uuid4()), path, v))

    with db() as con:
        # delete prior extracted fields for doc (v0.1 keeps only latest)
        con.execute("DELETE FROM extracted_fields WHERE document_id=?", (doc_id,))
        for row_id, path, v in rows:
            con.execute(
                """INSERT INTO extracted_fields (id, document_id, section_id, field_path, field_value, confidence)
                   VALUES (?, ?, ?, ?, ?, NULL)""",
                (row_id, doc_id, section_id, path, v),
            )


def store_1099da_transactions(*, doc_id: str, extraction: dict[str, Any]) -> None:
    txns = extraction.get("transactions") or []
    if not isinstance(txns, list):
        return
    with db() as con:
        con.execute("DELETE FROM transactions_1099da WHERE document_id=?", (doc_id,))
        for t in txns:
            if not isinstance(t, dict):
                continue
            con.execute(
                """INSERT INTO transactions_1099da (
                    id, document_id, asset_code, asset_name, units, date_acquired, date_sold,
                    proceeds, cost_basis, accrued_market_discount, wash_sale_disallowed,
                    basis_reported_to_irs, proceeds_type, qof_proceeds, federal_withheld,
                    loss_not_allowed, gain_loss_term, cash_only, customer_info_used,
                    noncovered, aggregate_flag, transaction_count, nft_first_sale_proceeds,
                    units_transferred_in, transfer_in_date, form_8949_code, state_name,
                    state_id, state_withheld, confidence, raw_json
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    str(uuid.uuid4()),
                    doc_id,
                    t.get("asset_code"),
                    t.get("asset_name"),
                    t.get("units"),
                    t.get("date_acquired"),
                    t.get("date_sold"),
                    t.get("proceeds"),
                    t.get("cost_basis"),
                    t.get("accrued_market_discount"),
                    t.get("wash_sale_disallowed"),
                    _bool_to_int(t.get("basis_reported_to_irs")),
                    t.get("proceeds_type"),
                    _bool_to_int(t.get("qof_proceeds")),
                    t.get("federal_withheld"),
                    _bool_to_int(t.get("loss_not_allowed")),
                    t.get("gain_loss_term"),
                    _bool_to_int(t.get("cash_only")),
                    _bool_to_int(t.get("customer_info_used")),
                    _bool_to_int(t.get("noncovered")),
                    t.get("aggregate_flag"),
                    t.get("transaction_count"),
                    t.get("nft_first_sale_proceeds"),
                    t.get("units_transferred_in"),
                    t.get("transfer_in_date"),
                    t.get("form_8949_code"),
                    t.get("state_name"),
                    t.get("state_id"),
                    t.get("state_withheld"),
                    t.get("confidence"),
                    json_dumps(t),
                ),
            )


def mark_processed(
    *,
    doc_id: str,
    overall_confidence: float | None = None,
    needs_review: bool | None = None,
    notes: str | None = None,
) -> None:
    with db() as con:
        con.execute(
            """UPDATE documents
               SET status='processed', extracted_at=?,
                   overall_confidence=COALESCE(?, overall_confidence),
                   needs_review=COALESCE(?, needs_review),
                   notes=COALESCE(?, notes)
               WHERE id=?""",
            (_utc_now_iso(), overall_confidence, int(needs_review) if needs_review is not None else None, notes, doc_id),
        )


def mark_needs_review(*, doc_id: str, notes: str | None = None) -> None:
    with db() as con:
        con.execute(
            "UPDATE documents SET status='needs_review', needs_review=1, extracted_at=?, notes=COALESCE(?, notes) WHERE id=?",
            (_utc_now_iso(), notes, doc_id),
        )


def mark_error(*, doc_id: str, error: str) -> None:
    # Keep errors short/UI-friendly; full stack traces are not shown.
    msg = " ".join(str(error).strip().split())
    if len(msg) > 500:
        msg = msg[:500].rstrip() + "…"
    with db() as con:
        con.execute(
            "UPDATE documents SET status='error', extracted_at=?, notes=COALESCE(?, notes) WHERE id=?",
            (_utc_now_iso(), msg, doc_id),
        )


_MISSING = object()


def update_document_metadata(
    *,
    doc_id: str,
    filer: str | None,
    tax_year: int | None,
    doc_type: str | None,
    notes: str | None,
    display_name: str | None | object = _MISSING,
) -> None:
    q = (
        """UPDATE documents
               SET filer=COALESCE(?, filer),
                   tax_year=COALESCE(?, tax_year),
                   doc_type=COALESCE(?, doc_type),
                   notes=COALESCE(?, notes)"""
    )
    params: list[Any] = [filer, tax_year, doc_type, notes]

    if display_name is not _MISSING:
        q += ", display_name=?"
        params.append(display_name)

    q += " WHERE id=?"
    params.append(doc_id)

    with db() as con:
        con.execute(q, tuple(params))


def _clean_payer_name(payer: str) -> str:
    # Collapse whitespace
    s = " ".join(payer.strip().split())
    if not s:
        return s

    # Title-case, but preserve common all-caps abbreviations.
    parts: list[str] = []
    for tok in s.split(" "):
        if tok.isupper() and len(tok) <= 4:
            parts.append(tok)
        else:
            parts.append(tok[:1].upper() + tok[1:].lower() if tok else tok)
    s2 = " ".join(parts)

    # Hard max length (UI-friendly)
    if len(s2) > 40:
        s2 = s2[:40].rstrip()
    return s2


def generate_display_name(*, payer: str | None, doc_type: str | None, tax_year: int | None) -> str | None:
    dt = (doc_type or "").strip()
    if not dt:
        return None

    yr = str(tax_year) if tax_year else ""
    p = _clean_payer_name(payer) if isinstance(payer, str) else ""

    if p and yr:
        return f"{p} — {dt} — {yr}"
    if p:
        return f"{p} — {dt}"
    if yr:
        return f"{dt} — {yr}"
    return dt


def set_display_name_if_empty(*, doc_id: str, display_name: str | None) -> None:
    if not display_name:
        return
    with db() as con:
        con.execute(
            """UPDATE documents
               SET display_name=?
               WHERE id=? AND (display_name IS NULL OR TRIM(display_name)='')""",
            (display_name, doc_id),
        )


def delete_document(doc_id: str) -> None:
    with db() as con:
        r = con.execute("SELECT file_path FROM documents WHERE id=?", (doc_id,)).fetchone()
        file_path = r[0] if r else None
        con.execute("DELETE FROM documents WHERE id=?", (doc_id,))

    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass


def page_count_for_pdf(path: str) -> int:
    doc = fitz.open(path)
    try:
        return doc.page_count
    finally:
        doc.close()


def _bool_to_int(v: Any) -> int | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return 1 if v else 0
    if isinstance(v, (int, float)):
        return 1 if v else 0
    return None
