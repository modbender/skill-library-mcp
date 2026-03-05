#!/usr/bin/env python3
"""
AgxntSix Structured Database — SQLite for projects, contacts, tasks, research
Usage:
  structured_db.py init                         # Create tables
  structured_db.py query "SELECT ..."           # Raw SQL query  
  structured_db.py insert <table> '{"col":"val"}'  # Insert row
  structured_db.py tables                       # List tables with counts
"""
import argparse
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.expanduser("~/.openclaw/workspace/.data/sqlite/agxntsix.db")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db(args=None):
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            description TEXT,
            notes TEXT,
            tags TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            handle TEXT,
            email TEXT,
            phone TEXT,
            platform TEXT,
            company TEXT,
            notes TEXT,
            tags TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER REFERENCES projects(id),
            title TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'normal',
            due_date TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            source_url TEXT,
            source_type TEXT,
            summary TEXT,
            full_text TEXT,
            tags TEXT,
            project_id INTEGER REFERENCES projects(id),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            tags TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            metadata TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    print(json.dumps({"status": "initialized", "db": DB_PATH}))

def run_query(args):
    conn = get_conn()
    try:
        cursor = conn.execute(args.sql)
        if args.sql.strip().upper().startswith("SELECT"):
            rows = [dict(row) for row in cursor.fetchall()]
            print(json.dumps(rows, indent=2, default=str))
        else:
            conn.commit()
            print(json.dumps({"status": "ok", "rows_affected": cursor.rowcount}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

def insert_row(args):
    conn = get_conn()
    data = json.loads(args.data)
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    try:
        cursor = conn.execute(f"INSERT INTO {args.table} ({cols}) VALUES ({placeholders})", list(data.values()))
        conn.commit()
        print(json.dumps({"status": "inserted", "id": cursor.lastrowid, "table": args.table}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

def list_tables(args=None):
    conn = get_conn()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row["name"] for row in cursor.fetchall()]
    result = {}
    for table in tables:
        cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
        result[table] = cursor.fetchone()["count"]
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgxntSix Structured DB")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("init")
    q = sub.add_parser("query")
    q.add_argument("sql")
    i = sub.add_parser("insert")
    i.add_argument("table")
    i.add_argument("data")
    sub.add_parser("tables")
    
    args = parser.parse_args()
    commands = {"init": init_db, "query": run_query, "insert": insert_row, "tables": list_tables}
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
