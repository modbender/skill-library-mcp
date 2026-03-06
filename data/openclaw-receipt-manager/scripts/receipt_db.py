#!/usr/bin/env python3
"""
Receipt manager DB + ingestion CLI.

Usage examples:
  python3 scripts/receipt_db.py init
  python3 scripts/receipt_db.py add --image ~/Downloads/r.jpg --text "Green Fresh Supermarket Total $2.47 2026-02-26"
  python3 scripts/receipt_db.py add --image ~/Downloads/r.jpg
  python3 scripts/receipt_db.py search --q grocery
  python3 scripts/receipt_db.py show --id 1
  python3 scripts/receipt_db.py summary --month 2026-02
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "receipts"
DB_PATH = DATA_DIR / "db.sqlite3"
IMG_DIR = DATA_DIR / "images"

CATEGORIES = {
    "grocery": ["supermarket", "grocery", "freshco", "whole foods", "costco", "market", "mart", "trader joe", "save on"],
    "dining": ["restaurant", "cafe", "coffee", "tea", "diner", "pizza", "burger", "sushi", "bbq", "kitchen"],
    "transport": ["uber", "lyft", "taxi", "gas", "fuel", "petro", "shell", "chevron", "parking", "transit"],
    "health": ["pharmacy", "drug", "clinic", "hospital", "dental", "health", "medicine"],
    "shopping": ["amazon", "walmart", "target", "store", "shop", "mall", "ikea", "best buy"],
    "travel": ["hotel", "airbnb", "airlines", "flight", "booking", "expedia"],
    "utilities": ["hydro", "electric", "internet", "phone", "water", "utility", "telus", "rogers", "bell"],
}

DATE_PATTERNS = [
    re.compile(r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b"),  # YYYY-MM-DD
    re.compile(r"\b(\d{1,2})[-/](\d{1,2})[-/](20\d{2})\b"),  # MM/DD/YYYY
]

AMOUNT_PATTERNS = [
    re.compile(r"(?i)(?:total|amount|sum)\s*[:：]?\s*([\$€£¥]?\s?\d+[\.,]\d{2})"),
    re.compile(r"([\$€£¥]\s?\d+[\.,]\d{2})"),
]


def ensure_dirs() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)


def connect() -> sqlite3.Connection:
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(verbose: bool = False) -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS receipts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_at TEXT NOT NULL,
              vendor TEXT,
              receipt_date TEXT,
              currency TEXT,
              total REAL,
              category TEXT,
              image_path TEXT NOT NULL,
              image_sha256 TEXT NOT NULL UNIQUE,
              ocr_text TEXT,
              items_json TEXT,
              meta_json TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_receipts_date ON receipts(receipt_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_receipts_vendor ON receipts(vendor)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_receipts_category ON receipts(category)")

        cols = {r[1] for r in conn.execute("PRAGMA table_info(receipts)").fetchall()}
        if "items_json" not in cols:
            conn.execute("ALTER TABLE receipts ADD COLUMN items_json TEXT")
    if verbose:
        print(f"Initialized: {DB_PATH}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_image_dedup(src: Path) -> tuple[str, str]:
    ext = src.suffix.lower() or ".jpg"
    digest = sha256_file(src)
    dst = IMG_DIR / f"{digest}{ext}"
    if not dst.exists():
        shutil.copy2(src, dst)
    rel = str(dst.relative_to(ROOT))
    return rel, digest


def try_ocr_tesseract(image: Path) -> Optional[str]:
    tesseract = shutil.which("tesseract")
    if not tesseract:
        return None
    try:
        proc = subprocess.run(
            [tesseract, str(image), "stdout", "-l", "eng+chi_sim"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=30,
        )
        if proc.returncode == 0:
            txt = (proc.stdout or "").strip()
            return txt or None
    except Exception:
        pass
    return None


def normalize_date(text: str) -> Optional[str]:
    for idx, pat in enumerate(DATE_PATTERNS):
        m = pat.search(text)
        if not m:
            continue
        try:
            if idx == 0:
                y, mo, d = map(int, m.groups())
            else:
                mo, d, y = map(int, m.groups())
            return dt.date(y, mo, d).isoformat()
        except Exception:
            continue
    return None


def parse_total_and_currency(text: str) -> tuple[Optional[float], Optional[str]]:
    for pat in AMOUNT_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        raw = m.group(1).replace(" ", "")
        currency = None
        if raw and raw[0] in "$€£¥":
            currency = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "CNY"}.get(raw[0], None)
            raw = raw[1:]
        raw = raw.replace(",", ".")
        try:
            return float(raw), currency
        except Exception:
            pass
    return None, None


def parse_vendor(text: str) -> Optional[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return None
    for ln in lines[:6]:
        if re.search(r"(?i)receipt|invoice|tax|total|date|thank", ln):
            continue
        if 2 <= len(ln) <= 48:
            return ln
    return lines[0][:48]


def auto_category(vendor: Optional[str], text: str) -> str:
    blob = f"{vendor or ''} {text}".lower()
    for cat, kws in CATEGORIES.items():
        if any(kw in blob for kw in kws):
            return cat
    return "other"


def parse_items(text: str) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or len(line) < 3:
            continue
        m = re.search(r"(.+?)\s+([\$€£¥]?\d+[\.,]\d{2})$", line)
        if not m:
            continue
        name = m.group(1).strip(" -:\t")
        price_raw = m.group(2).replace(" ", "")
        currency = None
        if price_raw[0] in "$€£¥":
            currency = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "CNY"}.get(price_raw[0])
            price_raw = price_raw[1:]
        try:
            price = float(price_raw.replace(",", "."))
        except Exception:
            continue
        if name and not re.search(r"(?i)total|subtotal|tax|amount|sum", name):
            items.append({"name": name[:120], "price": price, "currency": currency})
    return items


def add_receipt(args: argparse.Namespace) -> int:
    image = Path(args.image).expanduser().resolve()
    
    # Security: prevent path traversal
    if '..' in str(image):
        print("ERROR: invalid image path (path traversal)")
        return 2
    
    # Validate image is within allowed directory (home only for security)
    if not image.is_relative_to(Path.home()):
        print(f"ERROR: image must be in home directory: {image}")
        return 2
    
    if not image.exists():
        print(f"ERROR: image not found: {image}")
        return 2

    init_db()
    rel_image, digest = copy_image_dedup(image)

    ocr_text = args.text.strip() if args.text else None
    ocr_engine = None
    if not ocr_text:
        ocr_text = try_ocr_tesseract(image)
        if ocr_text:
            ocr_engine = "tesseract"

    text_for_parse = ocr_text or ""
    vendor = args.vendor or parse_vendor(text_for_parse)
    receipt_date = args.date or normalize_date(text_for_parse)
    total, currency = (None, None)
    if args.total is not None:
        total = float(args.total)
    else:
        total, currency = parse_total_and_currency(text_for_parse)
    if args.currency:
        currency = args.currency.upper()

    category = args.category or auto_category(vendor, text_for_parse)
    parsed_items = []
    if args.items_json:
        try:
            parsed_items = json.loads(args.items_json)
        except Exception:
            parsed_items = []
    elif text_for_parse:
        parsed_items = parse_items(text_for_parse)

    meta = {
        "ocr_engine": ocr_engine,
        "ocr_available": bool(ocr_text),
        "source_image": str(image),
    }

    with connect() as conn:
        row = conn.execute("SELECT id FROM receipts WHERE image_sha256 = ?", (digest,)).fetchone()
        if row:
            print(json.dumps({"status": "duplicate", "receipt_id": row["id"], "image": rel_image}, ensure_ascii=False, indent=2))
            return 0

        cur = conn.execute(
            """
            INSERT INTO receipts(
                created_at, vendor, receipt_date, currency, total, category,
                image_path, image_sha256, ocr_text, items_json, meta_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                vendor,
                receipt_date,
                currency,
                total,
                category,
                rel_image,
                digest,
                ocr_text,
                json.dumps(parsed_items, ensure_ascii=False),
                json.dumps(meta, ensure_ascii=False),
            ),
        )
        rid = cur.lastrowid

    out = {
        "status": "ok",
        "receipt_id": rid,
        "vendor": vendor,
        "date": receipt_date,
        "total": total,
        "currency": currency,
        "category": category,
        "image": rel_image,
        "db": str(DB_PATH.relative_to(ROOT)),
        "ocr": "provided" if args.text else ("tesseract" if ocr_engine else "none"),
        "item_count": len(parsed_items),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def search_receipts(args: argparse.Namespace) -> int:
    init_db()
    q = (args.q or "").strip()
    item = (args.item or "").strip()
    clauses = []
    params: list[object] = []
    if q:
        like = f"%{q}%"
        clauses.append("(vendor LIKE ? OR category LIKE ? OR ocr_text LIKE ? OR items_json LIKE ?)")
        params.extend([like, like, like, like])
    if item:
        clauses.append("items_json LIKE ?")
        params.append(f"%{item}%")
    wh = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT id, receipt_date, vendor, total, currency, category, image_path, items_json FROM receipts {wh} ORDER BY id DESC LIMIT ?"
    params.append(args.limit)
    with connect() as conn:
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def show_receipt(args: argparse.Namespace) -> int:
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT * FROM receipts WHERE id = ?", (args.id,)).fetchone()
    if not row:
        print(f"Not found: {args.id}")
        return 1
    d = dict(row)
    if d.get("meta_json"):
        try:
            d["meta_json"] = json.loads(d["meta_json"])
        except Exception:
            pass
    if d.get("items_json"):
        try:
            d["items_json"] = json.loads(d["items_json"])
        except Exception:
            pass
    print(json.dumps(d, ensure_ascii=False, indent=2))
    return 0


def summary(args: argparse.Namespace) -> int:
    init_db()
    month = args.month or dt.date.today().strftime("%Y-%m")
    if not re.match(r"^20\d{2}-\d{2}$", month):
        print("month must be YYYY-MM")
        return 2

    like = f"{month}-%"
    with connect() as conn:
        by_cat = [
            dict(r)
            for r in conn.execute(
                """
                SELECT category, COUNT(*) AS count, ROUND(COALESCE(SUM(total),0),2) AS total
                FROM receipts
                WHERE receipt_date LIKE ?
                GROUP BY category
                ORDER BY total DESC
                """,
                (like,),
            ).fetchall()
        ]
        by_vendor = [
            dict(r)
            for r in conn.execute(
                """
                SELECT COALESCE(vendor, 'Unknown') AS vendor, COUNT(*) AS count, ROUND(COALESCE(SUM(total),0),2) AS total
                FROM receipts
                WHERE receipt_date LIKE ?
                GROUP BY COALESCE(vendor, 'Unknown')
                ORDER BY total DESC
                LIMIT ?
                """,
                (like, args.vendor_limit),
            ).fetchall()
        ]
    print(json.dumps({"month": month, "by_category": by_cat, "by_vendor": by_vendor}, ensure_ascii=False, indent=2))
    return 0


def list_receipts(args: argparse.Namespace) -> int:
    init_db()
    clauses = []
    params: list[object] = []
    if args.month:
        if re.match(r"^\d{1,2}$", args.month):
            y = dt.date.today().year
            m = int(args.month)
            month = f"{y}-{m:02d}"
        else:
            month = args.month
        clauses.append("receipt_date LIKE ?")
        params.append(f"{month}-%")
    if args.category:
        clauses.append("LOWER(category)=LOWER(?)")
        params.append(args.category)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT id, receipt_date, vendor, total, currency, category, items_json FROM receipts {where} ORDER BY receipt_date DESC, id DESC LIMIT ?"
    params.append(args.limit)
    with connect() as conn:
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def nlp_query(args: argparse.Namespace) -> int:
    init_db()
    t = (args.text or "").strip()
    if not t:
        print(json.dumps({"status": "error", "message": "empty text"}, ensure_ascii=False, indent=2))
        return 2

    m = re.search(r"查\s*(.+?)\s*在.*收据", t)
    if m:
        item = m.group(1).strip()
        ns = argparse.Namespace(q="", item=item, limit=args.limit)
        return search_receipts(ns)

    m2 = re.search(r"列出\s*(\d{1,2})\s*月\s*(\S+?)类?收据", t)
    if m2:
        month = m2.group(1)
        cat = m2.group(2)
        ns = argparse.Namespace(month=month, category=cat, limit=args.limit)
        return list_receipts(ns)

    if "汇总" in t and re.search(r"\d{4}-\d{2}", t):
        month = re.search(r"(\d{4}-\d{2})", t).group(1)
        ns = argparse.Namespace(month=month, vendor_limit=10)
        return summary(ns)

    print(json.dumps({
        "status": "unrecognized",
        "hint": [
            "查吹风机在哪个收据",
            "列出2月购物类收据",
            "汇总 2026-02"
        ]
    }, ensure_ascii=False, indent=2))
    return 0


def update_receipt(args: argparse.Namespace) -> int:
    init_db()
    updates: dict[str, object] = {}

    if args.vendor is not None:
        updates["vendor"] = args.vendor
    if args.date is not None:
        updates["receipt_date"] = args.date
    if args.total is not None:
        updates["total"] = float(args.total)
    if args.currency is not None:
        updates["currency"] = args.currency.upper() if args.currency else None
    if args.category is not None:
        updates["category"] = args.category
    if args.text is not None:
        updates["ocr_text"] = args.text
    if args.items_json is not None:
        try:
            json.loads(args.items_json)
            updates["items_json"] = args.items_json
        except Exception:
            print("--items-json must be valid JSON array")
            return 2

    if not updates:
        print("No fields to update. Provide at least one of --vendor/--date/--total/--currency/--category/--text/--items-json")
        return 2

    cols = ", ".join([f"{k} = ?" for k in updates.keys()])
    params = list(updates.values()) + [args.id]

    with connect() as conn:
        row = conn.execute("SELECT id FROM receipts WHERE id = ?", (args.id,)).fetchone()
        if not row:
            print(f"Not found: {args.id}")
            return 1
        conn.execute(f"UPDATE receipts SET {cols} WHERE id = ?", params)

    print(json.dumps({"status": "ok", "updated_id": args.id, "fields": list(updates.keys())}, ensure_ascii=False, indent=2))
    return 0


def delete_receipt(args: argparse.Namespace) -> int:
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT id, image_path FROM receipts WHERE id = ?", (args.id,)).fetchone()
        if not row:
            print(f"Not found: {args.id}")
            return 1

        if not args.yes:
            print(json.dumps({
                "status": "confirm_required",
                "id": args.id,
                "hint": "re-run with --yes to confirm deletion"
            }, ensure_ascii=False, indent=2))
            return 2

        conn.execute("DELETE FROM receipts WHERE id = ?", (args.id,))

    if args.delete_image and row["image_path"]:
        img = ROOT / row["image_path"]
        try:
            if img.exists():
                img.unlink()
        except Exception:
            pass

    print(json.dumps({
        "status": "ok",
        "deleted_id": args.id,
        "image_deleted": bool(args.delete_image)
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Receipt manager CLI")
    sp = p.add_subparsers(dest="cmd", required=True)

    sp.add_parser("init", help="Initialize DB")

    p_add = sp.add_parser("add", help="Add one receipt")
    p_add.add_argument("--image", required=True, help="Path to receipt image")
    p_add.add_argument("--text", help="Optional OCR text (if omitted, tries local OCR)")
    p_add.add_argument("--vendor")
    p_add.add_argument("--date", help="YYYY-MM-DD")
    p_add.add_argument("--total", type=float)
    p_add.add_argument("--currency", help="USD/CAD/CNY...")
    p_add.add_argument("--category", help="grocery/dining/.../other")
    p_add.add_argument("--items-json", help="JSON array of items, e.g. [{\"name\":\"dryer\",\"price\":99.0}]")

    p_search = sp.add_parser("search", help="Search receipts")
    p_search.add_argument("--q", default="")
    p_search.add_argument("--item", default="", help="Search in items_json by item keyword")
    p_search.add_argument("--limit", type=int, default=20)

    p_show = sp.add_parser("show", help="Show receipt by id")
    p_show.add_argument("--id", type=int, required=True)

    p_sum = sp.add_parser("summary", help="Monthly summary")
    p_sum.add_argument("--month", help="YYYY-MM")
    p_sum.add_argument("--vendor-limit", type=int, default=10)

    p_list = sp.add_parser("list", help="List receipts with filters")
    p_list.add_argument("--month", help="YYYY-MM or M")
    p_list.add_argument("--category", help="category filter")
    p_list.add_argument("--limit", type=int, default=20)

    p_nlp = sp.add_parser("nlp", help="Natural language query helper")
    p_nlp.add_argument("--text", required=True, help="e.g. 查吹风机在哪个收据")
    p_nlp.add_argument("--limit", type=int, default=20)

    p_upd = sp.add_parser("update", help="Update receipt fields")
    p_upd.add_argument("--id", type=int, required=True)
    p_upd.add_argument("--vendor")
    p_upd.add_argument("--date", help="YYYY-MM-DD")
    p_upd.add_argument("--total", type=float)
    p_upd.add_argument("--currency")
    p_upd.add_argument("--category")
    p_upd.add_argument("--text", help="Replace OCR text")
    p_upd.add_argument("--items-json", help="Replace items_json with a JSON array")

    p_del = sp.add_parser("delete", help="Delete receipt by id")
    p_del.add_argument("--id", type=int, required=True)
    p_del.add_argument("--yes", action="store_true", help="Confirm deletion")
    p_del.add_argument("--delete-image", action="store_true", help="Also delete stored image file")

    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.cmd == "init":
        init_db(verbose=True)
        return 0
    if args.cmd == "add":
        return add_receipt(args)
    if args.cmd == "search":
        return search_receipts(args)
    if args.cmd == "show":
        return show_receipt(args)
    if args.cmd == "summary":
        return summary(args)
    if args.cmd == "list":
        return list_receipts(args)
    if args.cmd == "nlp":
        return nlp_query(args)
    if args.cmd == "update":
        return update_receipt(args)
    if args.cmd == "delete":
        return delete_receipt(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
