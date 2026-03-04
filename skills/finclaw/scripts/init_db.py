#!/usr/bin/env python3
"""Initialize the FinClaw SQLite database schema."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.db import get_connection

SCHEMA = """
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    name TEXT,
    asset_type TEXT NOT NULL CHECK(asset_type IN ('stock_us','stock_bist','crypto','forex')),
    currency TEXT NOT NULL DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('buy','sell')),
    shares REAL NOT NULL,
    price REAL NOT NULL,
    fees REAL DEFAULT 0,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    condition TEXT NOT NULL CHECK(condition IN ('above','below','change_pct','volume_above')),
    target_value REAL NOT NULL,
    current_value_at_creation REAL,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','triggered','snoozed','deleted')),
    triggered_at TIMESTAMP,
    snoozed_until TIMESTAMP,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS watchlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS watchlist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    watchlist_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    FOREIGN KEY (watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE,
    UNIQUE(watchlist_id, symbol)
);

CREATE TABLE IF NOT EXISTS price_cache (
    symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    price REAL NOT NULL,
    change REAL,
    change_pct REAL,
    volume REAL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, asset_type)
);

CREATE TABLE IF NOT EXISTS briefing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    briefing_type TEXT NOT NULL,
    content_hash TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


if __name__ == "__main__":
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    print(f"Database initialized. Tables: {', '.join(r['name'] for r in tables)}")
    conn.close()
