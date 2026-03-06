from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .config import load_config


SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  file_path TEXT NOT NULL,
  file_hash TEXT NOT NULL UNIQUE,
  original_filename TEXT,
  mime_type TEXT,

  tax_year INTEGER,
  doc_type TEXT,
  filer TEXT,

  payer_name TEXT,
  payer_tin TEXT,
  display_name TEXT,
  recipient_name TEXT,
  recipient_tin TEXT,
  account_number TEXT,

  page_count INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  extracted_at TEXT,

  classification_confidence REAL,
  overall_confidence REAL,

  needs_review INTEGER NOT NULL DEFAULT 0,
  status TEXT DEFAULT 'received',
  notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_documents_tax_year ON documents(tax_year);
CREATE INDEX IF NOT EXISTS idx_documents_doc_type ON documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_documents_needs_review ON documents(needs_review);

CREATE TABLE IF NOT EXISTS form_sections (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL,

  form_type TEXT NOT NULL,
  section_page_start INTEGER,
  section_page_end INTEGER,

  raw_json TEXT,
  confidence REAL,

  created_at TEXT NOT NULL DEFAULT (datetime('now')),

  FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_form_sections_document_id ON form_sections(document_id);

-- Generic normalized extracted fields table
CREATE TABLE IF NOT EXISTS extracted_fields (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL,
  section_id TEXT,

  field_path TEXT NOT NULL,             -- e.g. 'payer_name' or 'transactions[0].proceeds'
  field_value TEXT,
  confidence REAL,

  created_at TEXT NOT NULL DEFAULT (datetime('now')),

  FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
  FOREIGN KEY(section_id) REFERENCES form_sections(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_extracted_fields_document_id ON extracted_fields(document_id);
CREATE INDEX IF NOT EXISTS idx_extracted_fields_field_path ON extracted_fields(field_path);

-- Legacy/raw extraction storage (kept for audit/debug)
CREATE TABLE IF NOT EXISTS form_extractions (
  id TEXT PRIMARY KEY,
  document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
  form_type TEXT NOT NULL,
  raw_json TEXT,
  confidence REAL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- v0.1 typed table for 1099-DA transactions
CREATE TABLE IF NOT EXISTS transactions_1099da (
  id TEXT PRIMARY KEY,
  document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
  asset_code TEXT,
  asset_name TEXT,
  units TEXT,
  date_acquired TEXT,
  date_sold TEXT,
  proceeds TEXT,
  cost_basis TEXT,
  accrued_market_discount TEXT,
  wash_sale_disallowed TEXT,
  basis_reported_to_irs INTEGER,
  proceeds_type TEXT,
  qof_proceeds INTEGER,
  federal_withheld TEXT,
  loss_not_allowed INTEGER,
  gain_loss_term TEXT,
  cash_only INTEGER,
  customer_info_used INTEGER,
  noncovered INTEGER,
  aggregate_flag TEXT,
  transaction_count INTEGER,
  nft_first_sale_proceeds TEXT,
  units_transferred_in TEXT,
  transfer_in_date TEXT,
  form_8949_code TEXT,
  state_name TEXT,
  state_id TEXT,
  state_withheld TEXT,
  confidence REAL,
  raw_json TEXT
);

CREATE TABLE IF NOT EXISTS review_queue (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL,

  field_path TEXT NOT NULL,
  extracted_value TEXT,
  confidence REAL,

  resolved INTEGER NOT NULL DEFAULT 0,
  corrected_value TEXT,
  resolved_at TEXT,

  created_at TEXT NOT NULL DEFAULT (datetime('now')),

  FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_review_queue_document_id ON review_queue(document_id);
CREATE INDEX IF NOT EXISTS idx_review_queue_resolved ON review_queue(resolved);
"""


def _db_path() -> Path:
    cfg = load_config()
    return cfg.db_path


def connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA foreign_keys=ON;")
    return con


def init_db() -> None:
    con = connect()
    try:
        con.executescript(SCHEMA)

        # Lightweight migrations for existing DBs.
        cols = [r[1] for r in con.execute("PRAGMA table_info(documents)").fetchall()]
        if "display_name" not in cols:
            con.execute("ALTER TABLE documents ADD COLUMN display_name TEXT;")

        # Best-effort backfill for existing rows.
        con.execute(
            """UPDATE documents
               SET display_name = CASE
                 WHEN payer_name IS NOT NULL AND TRIM(payer_name) != '' AND tax_year IS NOT NULL
                   THEN payer_name || ' — ' || doc_type || ' — ' || tax_year
                 WHEN payer_name IS NOT NULL AND TRIM(payer_name) != ''
                   THEN payer_name || ' — ' || doc_type
                 WHEN tax_year IS NOT NULL
                   THEN doc_type || ' — ' || tax_year
                 ELSE doc_type
               END
               WHERE (display_name IS NULL OR TRIM(display_name)='')
                 AND doc_type IS NOT NULL AND TRIM(doc_type) != ''
            """
        )

        con.commit()
    finally:
        con.close()


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    con = connect()
    try:
        yield con
        con.commit()
    finally:
        con.close()


def row_to_dict(r: sqlite3.Row | None) -> dict[str, Any] | None:
    if r is None:
        return None
    return {k: r[k] for k in r.keys()}


def json_dumps(v: Any) -> str:
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
