#!/usr/bin/env python3
"""SQLite database layer for the finance reconciler."""

import hashlib
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

DEFAULT_DATA_DIR = os.path.expanduser("~/.openclaw/skills/finance-reconciler/data")
DB_NAME = "transactions.db"


def get_db_path():
    data_dir = os.environ.get("FINANCE_DATA_DIR", DEFAULT_DATA_DIR)
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    return os.path.join(data_dir, DB_NAME)


def get_connection(db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def transaction_hash(date_str, description, amount):
    raw = f"{date_str}|{description}|{amount}"
    return hashlib.sha256(raw.encode()).hexdigest()


def init_db(conn=None):
    close = False
    if conn is None:
        conn = get_connection()
        close = True

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_hash TEXT UNIQUE NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            original_description TEXT,
            amount REAL NOT NULL,
            category_id INTEGER,
            category_confidence REAL DEFAULT 0.0,
            account TEXT,
            source_file TEXT,
            transaction_type TEXT,
            memo TEXT,
            imported_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS categorization_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            rule_type TEXT NOT NULL CHECK(rule_type IN ('exact', 'keyword', 'regex', 'custom')),
            pattern TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            period TEXT NOT NULL CHECK(period IN ('monthly', 'yearly')),
            start_date TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (category_id) REFERENCES categories(id),
            UNIQUE(category_id, period)
        );

        CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
        CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_hash ON transactions(transaction_hash);
        CREATE INDEX IF NOT EXISTS idx_categorization_rules_category ON categorization_rules(category_id);
    """)
    conn.commit()

    if close:
        conn.close()


def seed_categories(conn=None):
    close = False
    if conn is None:
        conn = get_connection()
        close = True

    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    categories_file = os.path.join(assets_dir, "categories.json")

    with open(categories_file) as f:
        categories_data = json.load(f)

    for cat in categories_data["categories"]:
        conn.execute(
            "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
            (cat["name"], cat["description"]),
        )

        cat_row = conn.execute(
            "SELECT id FROM categories WHERE name = ?", (cat["name"],)
        ).fetchone()
        cat_id = cat_row["id"]

        for keyword in cat.get("keywords", []):
            conn.execute(
                "INSERT OR IGNORE INTO categorization_rules (category_id, rule_type, pattern, priority) VALUES (?, 'keyword', ?, 0)",
                (cat_id, keyword.lower()),
            )

        for pattern in cat.get("patterns", []):
            conn.execute(
                "INSERT OR IGNORE INTO categorization_rules (category_id, rule_type, pattern, priority) VALUES (?, 'regex', ?, 0)",
                (cat_id, pattern),
            )

    conn.commit()
    if close:
        conn.close()


def ensure_db_ready(db_path=None):
    conn = get_connection(db_path)
    init_db(conn)
    cat_count = conn.execute("SELECT COUNT(*) as c FROM categories").fetchone()["c"]
    if cat_count == 0:
        seed_categories(conn)
    conn.close()


def insert_transaction(conn, date_str, description, amount, account=None,
                       source_file=None, transaction_type=None, memo=None,
                       original_description=None):
    tx_hash = transaction_hash(date_str, description, amount)
    try:
        conn.execute(
            """INSERT INTO transactions
               (transaction_hash, date, description, original_description, amount,
                account, source_file, transaction_type, memo)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (tx_hash, date_str, description, original_description or description,
             amount, account, source_file, transaction_type, memo),
        )
        return True
    except sqlite3.IntegrityError:
        return False


def get_transactions(conn, start_date=None, end_date=None, category=None,
                     account=None, limit=None):
    query = """
        SELECT t.*, c.name as category_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE 1=1
    """
    params = []

    if start_date:
        query += " AND t.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND t.date <= ?"
        params.append(end_date)
    if category:
        query += " AND c.name = ?"
        params.append(category)
    if account:
        query += " AND t.account = ?"
        params.append(account)

    query += " ORDER BY t.date DESC"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    return conn.execute(query, params).fetchall()


def get_category_id(conn, category_name):
    row = conn.execute(
        "SELECT id FROM categories WHERE name = ?", (category_name,)
    ).fetchone()
    return row["id"] if row else None


def get_all_categories(conn):
    return conn.execute("SELECT * FROM categories ORDER BY name").fetchall()


def get_categorization_rules(conn):
    return conn.execute("""
        SELECT r.*, c.name as category_name
        FROM categorization_rules r
        JOIN categories c ON r.category_id = c.id
        ORDER BY r.priority DESC, r.rule_type
    """).fetchall()


if __name__ == "__main__":
    ensure_db_ready()
    print(json.dumps({"success": True, "message": "Database initialized successfully",
                       "path": get_db_path()}))
