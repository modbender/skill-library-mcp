from __future__ import annotations

# CLI implementation imported by bin/taxclaw and bin/tax-extract.

import argparse
import sys
from pathlib import Path

from .classify import classify_document
from .config import load_config
from .db import init_db
from .exporter import (
    export_all_csv_long,
    export_all_csv_wide,
    export_all_json,
    export_doc_csv_long,
    export_doc_csv_wide,
    export_doc_json,
)
from .extract import extract_document
from .review import compute_needs_review, compute_overall_confidence, missing_required_fields
from .store import (
    create_document_record,
    get_document_by_hash,
    ingest_file,
    list_documents,
    mark_needs_review,
    mark_processed,
    page_count_for_pdf,
    store_1099da_transactions,
    store_extracted_fields,
    store_raw_extraction,
)


def cmd_ingest(args: argparse.Namespace) -> int:
    cfg = load_config()
    init_db()

    dest_path, file_hash, original_filename, mime_type = ingest_file(args.path, cfg)
    existing = get_document_by_hash(file_hash)
    if existing:
        print(existing["id"])
        return 0

    page_count = page_count_for_pdf(dest_path) if dest_path.lower().endswith(".pdf") else 1

    cls = classify_document(dest_path, cfg)
    doc_type = cls.get("doc_type") or "unknown"
    classification_confidence = float(cls.get("confidence") or 0.0)

    doc_id = create_document_record(
        cfg=cfg,
        file_path=dest_path,
        file_hash=file_hash,
        original_filename=original_filename,
        mime_type=mime_type,
        filer=args.filer,
        tax_year=args.year,
        doc_type=doc_type,
        page_count=page_count,
        classification_confidence=classification_confidence,
    )

    try:
        extracted = extract_document(dest_path, doc_type, cfg)
        section_id = store_raw_extraction(doc_id=doc_id, form_type=doc_type, data=extracted, confidence=classification_confidence)
        store_extracted_fields(doc_id=doc_id, section_id=section_id, data=extracted)
        if doc_type == "1099-DA" and isinstance(extracted, dict):
            store_1099da_transactions(doc_id=doc_id, extraction=extracted)

        missing = missing_required_fields(doc_type, extracted)
        overall = compute_overall_confidence(doc_type=doc_type, extraction=extracted, classification_confidence=classification_confidence)
        nr = compute_needs_review(classification_confidence=classification_confidence, overall_confidence=overall, missing_required=missing)
        mark_processed(doc_id=doc_id, overall_confidence=overall, needs_review=nr)
        if nr and missing:
            mark_needs_review(doc_id=doc_id, notes=f"missing required fields: {', '.join(missing)}")

    except Exception as e:
        mark_needs_review(doc_id=doc_id, notes=str(e))

    print(doc_id)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    init_db()
    docs = list_documents(filer=args.filer, year=args.year, doc_type=args.type, needs_review=args.needs_review)
    for d in docs:
        print(
            f"{d['id']}\t{d.get('doc_type')}\t{d.get('tax_year')}\t{d.get('filer')}\tneeds_review={d.get('needs_review')}\t{d.get('status')}"
        )
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    init_db()

    if args.all:
        if args.format == "wide":
            sys.stdout.write(export_all_csv_wide())
            return 0
        if args.format == "long":
            sys.stdout.write(export_all_csv_long())
            return 0
        if args.format == "json":
            sys.stdout.write(export_all_json())
            return 0
        raise SystemExit("unknown format")

    if not args.id:
        raise SystemExit("--id required unless --all")

    if args.format == "wide":
        sys.stdout.write(export_doc_csv_wide(args.id))
        return 0
    if args.format == "long":
        sys.stdout.write(export_doc_csv_long(args.id))
        return 0
    if args.format == "json":
        sys.stdout.write(export_doc_json(args.id))
        return 0

    raise SystemExit("unknown format")


def cmd_serve(args: argparse.Namespace) -> int:
    import os

    import uvicorn

    cfg = load_config()
    init_db()

    # run from skill root so templates/static resolve
    skill_dir = Path(__file__).resolve().parents[1]
    os.chdir(str(skill_dir))

    uvicorn.run("src.main:app", host="127.0.0.1", port=cfg.port, reload=True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="taxclaw")
    sp = p.add_subparsers(dest="cmd", required=True)

    p_ing = sp.add_parser("ingest", help="ingest + classify + extract")
    p_ing.add_argument("path")
    p_ing.add_argument("--filer", default=None)
    p_ing.add_argument("--year", type=int, default=None)
    p_ing.set_defaults(func=cmd_ingest)

    p_ls = sp.add_parser("list", help="list documents")
    p_ls.add_argument("--filer", default=None)
    p_ls.add_argument("--year", type=int, default=None)
    p_ls.add_argument("--type", default=None)
    p_ls.add_argument("--needs-review", type=int, choices=[0, 1], default=None)
    p_ls.set_defaults(func=cmd_list)

    p_ex = sp.add_parser("export", help="export wide/long CSV or JSON")
    p_ex.add_argument("--id", default=None)
    p_ex.add_argument("--all", action="store_true")
    p_ex.add_argument("--format", choices=["wide", "long", "json"], default="wide")
    p_ex.set_defaults(func=cmd_export)

    p_sv = sp.add_parser("serve", help="run web ui")
    p_sv.set_defaults(func=cmd_serve)

    return p


def main(argv: list[str] | None = None) -> int:
    p = build_parser()
    args = p.parse_args(argv)
    return int(args.func(args))
