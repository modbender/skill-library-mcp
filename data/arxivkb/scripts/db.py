"""
db.py — SQLite schema and operations for ArXivKB.

All timestamps UTC. WAL mode for concurrent reads.
Array columns (categories) stored as JSON text.
"""

import json
import os
import sqlite3
from typing import Any, Optional


DEFAULT_DATA_DIR = os.path.expanduser("~/Downloads/ArXivKB")


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

def open_db(db_path: Optional[str] = None, **kwargs) -> sqlite3.Connection:
    if db_path is None:
        db_path = os.path.join(
            os.environ.get("ARXIVKB_DATA_DIR", DEFAULT_DATA_DIR), "arxivkb.db"
        )
    conn = sqlite3.connect(db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=10000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS papers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    arxiv_id    TEXT    UNIQUE NOT NULL,
    title       TEXT    NOT NULL,
    abstract    TEXT,
    categories  TEXT,
    published   TEXT,
    status      TEXT    DEFAULT 'new',
    created_at  TEXT    DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS chunks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id    INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    section     TEXT,
    chunk_index INTEGER,
    text        TEXT NOT NULL,
    faiss_id    INTEGER,
    created_at  TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS translations (
    paper_id    INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    language    TEXT NOT NULL,
    abstract    TEXT NOT NULL,
    created_at  TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    PRIMARY KEY (paper_id, language)
);

CREATE TABLE IF NOT EXISTS categories (
    code        TEXT PRIMARY KEY,
    description TEXT,
    group_name  TEXT,
    enabled     INTEGER DEFAULT 0,
    added_at    TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_papers_status    ON papers(status);
CREATE INDEX IF NOT EXISTS idx_papers_published ON papers(published);
CREATE INDEX IF NOT EXISTS idx_papers_created   ON papers(created_at);
CREATE INDEX IF NOT EXISTS idx_chunks_paper_id  ON chunks(paper_id);
CREATE INDEX IF NOT EXISTS idx_chunks_faiss_id  ON chunks(faiss_id);
"""


def init_db(db_path: Optional[str] = None, **kwargs) -> None:
    conn = open_db(db_path)
    try:
        for stmt in _SCHEMA_SQL.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(stmt)
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def _to_json(val) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, list):
        return json.dumps(val)
    return val if isinstance(val, str) else json.dumps(val)


def _from_json(val) -> Optional[list]:
    if val is None:
        return None
    if isinstance(val, list):
        return val
    try:
        parsed = json.loads(val)
        return parsed if isinstance(parsed, list) else [parsed]
    except (json.JSONDecodeError, TypeError):
        return None


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in ("categories",):
        if col in d:
            d[col] = _from_json(d[col])
    return d


def _rows_to_dicts(rows) -> list[dict]:
    return [_row_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

def get_categories(db_path: Optional[str] = None, enabled_only: bool = True) -> list[dict]:
    conn = open_db(db_path)
    try:
        if enabled_only:
            rows = conn.execute("SELECT code, description, group_name, enabled FROM categories WHERE enabled = 1 ORDER BY code").fetchall()
        else:
            rows = conn.execute("SELECT code, description, group_name, enabled FROM categories ORDER BY group_name, code").fetchall()
        return [{"code": r[0], "description": r[1] or "", "group_name": r[2] or "", "enabled": bool(r[3])} for r in rows]
    finally:
        conn.close()


def add_categories(codes: list[str], descriptions: dict[str, str] | None = None,
                   db_path: Optional[str] = None) -> tuple[list[str], list[str]]:
    conn = open_db(db_path)
    descs = descriptions or {}
    enabled, already = [], []
    try:
        for code in codes:
            row = conn.execute("SELECT enabled FROM categories WHERE code = ?", (code,)).fetchone()
            if row:
                if row[0]:
                    already.append(code)
                else:
                    conn.execute("UPDATE categories SET enabled = 1 WHERE code = ?", (code,))
                    enabled.append(code)
            else:
                desc = descs.get(code, "")
                conn.execute("INSERT INTO categories (code, description, enabled) VALUES (?, ?, 1)", (code, desc))
                enabled.append(code)
        conn.commit()
    finally:
        conn.close()
    return enabled, already


def remove_categories(codes: list[str], db_path: Optional[str] = None) -> tuple[list[str], list[str]]:
    conn = open_db(db_path)
    removed, not_found = [], []
    try:
        for code in codes:
            cur = conn.execute("UPDATE categories SET enabled = 0 WHERE code = ? AND enabled = 1", (code,))
            if cur.rowcount:
                removed.append(code)
            else:
                not_found.append(code)
        conn.commit()
    finally:
        conn.close()
    return removed, not_found


def seed_taxonomy(db_path: Optional[str] = None) -> int:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from arxiv_taxonomy import ARXIV_TAXONOMY
    conn = open_db(db_path)
    inserted = 0
    try:
        for group, cats in ARXIV_TAXONOMY.items():
            for code, desc in cats.items():
                try:
                    conn.execute(
                        "INSERT INTO categories (code, description, group_name, enabled) VALUES (?, ?, ?, 0)",
                        (code, desc, group))
                    inserted += 1
                except sqlite3.IntegrityError:
                    conn.execute(
                        "UPDATE categories SET description = COALESCE(NULLIF(description,''), ?), group_name = COALESCE(NULLIF(group_name,''), ?) WHERE code = ?",
                        (desc, group, code))
        conn.commit()
    finally:
        conn.close()
    return inserted


# ---------------------------------------------------------------------------
# Papers
# ---------------------------------------------------------------------------

def insert_paper(
    db_path: str,
    arxiv_id: str,
    title: str,
    abstract: Optional[str] = None,
    categories: Optional[list[str]] = None,
    published: Optional[str] = None,
    status: str = "new",
    **kwargs,
) -> int:
    """Insert a paper. Returns existing ID if arxiv_id already present."""
    conn = open_db(db_path)
    try:
        row = conn.execute("SELECT id FROM papers WHERE arxiv_id = ?", (arxiv_id,)).fetchone()
        if row:
            return row["id"]
        conn.execute(
            "INSERT INTO papers (arxiv_id, title, abstract, categories, published, status) VALUES (?, ?, ?, ?, ?, ?)",
            (arxiv_id, title, abstract, _to_json(categories), published, status),
        )
        conn.commit()
        return conn.execute("SELECT id FROM papers WHERE arxiv_id = ?", (arxiv_id,)).fetchone()["id"]
    finally:
        conn.close()


def get_paper(db_path: str, arxiv_id: str) -> Optional[dict]:
    conn = open_db(db_path)
    try:
        row = conn.execute("SELECT * FROM papers WHERE arxiv_id = ?", (arxiv_id,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def pdf_path_for(arxiv_id: str, data_dir: str) -> str:
    """Derive PDF path: {data_dir}/pdfs/{arxiv_id}.pdf"""
    return os.path.join(os.path.expanduser(data_dir), "pdfs", f"{arxiv_id}.pdf")


def update_paper_status(db_path: str, arxiv_id: str, status: str) -> None:
    conn = open_db(db_path)
    try:
        conn.execute("UPDATE papers SET status=? WHERE arxiv_id=?", (status, arxiv_id))
        conn.commit()
    finally:
        conn.close()


def list_papers(db_path: str, status: Optional[str] = None, limit: int = 50, order_by: str = "published DESC") -> list[dict]:
    conn = open_db(db_path)
    try:
        where = "WHERE status = ?" if status else ""
        params: list[Any] = [status] if status else []
        params.append(limit)
        rows = conn.execute(f"SELECT * FROM papers {where} ORDER BY {order_by} LIMIT ?", params).fetchall()
        return _rows_to_dicts(rows)
    finally:
        conn.close()


def get_papers_older_than(db_path: str, days: int) -> list[dict]:
    conn = open_db(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM papers WHERE created_at < strftime('%Y-%m-%dT%H:%M:%SZ', 'now', ?)",
            (f"-{days} days",),
        ).fetchall()
        return _rows_to_dicts(rows)
    finally:
        conn.close()


def delete_paper(db_path: str, paper_id: int) -> None:
    conn = open_db(db_path)
    try:
        conn.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def get_stats(db_path: Optional[str] = None) -> dict:
    conn = open_db(db_path)
    try:
        papers = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
        chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        embedded = conn.execute("SELECT COUNT(*) FROM chunks WHERE faiss_id IS NOT NULL").fetchone()[0]
        categories = conn.execute("SELECT COUNT(*) FROM categories WHERE enabled = 1").fetchone()[0]
        return {"papers": papers, "chunks": chunks, "embedded": embedded, "categories": categories}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Chunks
# ---------------------------------------------------------------------------

def insert_chunk(db_path: str, paper_id: int, section: str, chunk_index: int, text: str, **kwargs) -> int:
    conn = open_db(db_path)
    try:
        cursor = conn.execute(
            "INSERT INTO chunks (paper_id, section, chunk_index, text) VALUES (?, ?, ?, ?)",
            (paper_id, section, chunk_index, text),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_chunks_for_paper(db_path: str, paper_id: int) -> list[dict]:
    conn = open_db(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM chunks WHERE paper_id = ? ORDER BY chunk_index", (paper_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_unembedded_chunks(db_path: str) -> list[dict]:
    conn = open_db(db_path)
    try:
        rows = conn.execute(
            "SELECT c.id, c.text, p.arxiv_id, p.title FROM chunks c JOIN papers p ON c.paper_id = p.id WHERE c.faiss_id IS NULL"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_chunk_faiss_id(db_path: str, chunk_id: int, faiss_id: int) -> None:
    conn = open_db(db_path)
    try:
        conn.execute("UPDATE chunks SET faiss_id = ? WHERE id = ?", (faiss_id, chunk_id))
        conn.commit()
    finally:
        conn.close()


def get_chunks_by_faiss_ids(db_path: str, faiss_ids: list[int]) -> list[dict]:
    if not faiss_ids:
        return []
    conn = open_db(db_path)
    try:
        placeholders = ",".join("?" * len(faiss_ids))
        rows = conn.execute(
            f"""SELECT c.*, p.arxiv_id, p.title AS paper_title, p.published
                FROM chunks c JOIN papers p ON c.paper_id = p.id
                WHERE c.faiss_id IN ({placeholders})""",
            faiss_ids,
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
