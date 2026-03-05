#!/usr/bin/env python3
"""
Congress Trades Scraper — syncs politician trades from Quiver Quant API to SQLite.
Run via system cron (every minute recommended). Writes alerts for OpenClaw heartbeat pickup.

Configuration: edit the variables below or set environment variables.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

import requests

# ─── Config (override with env vars) ───────────────────────────────────────
API_BASE = "https://api.quiverquant.com/beta/live/congresstrading"
API_KEY = os.environ.get("QUIVER_API_KEY")
if not API_KEY:
    print("ERROR: QUIVER_API_KEY environment variable is required. Get one at https://www.quiverquant.com/")
    sys.exit(1)
MIN_TRADE_AMOUNT = int(os.environ.get("MIN_TRADE_AMOUNT", "15001"))

# Paths (relative to script location)
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_DIR, "data")
LOGS_DIR = os.path.join(SKILL_DIR, "logs")
DB_PATH = os.environ.get("CONGRESS_DB_PATH", os.path.join(DATA_DIR, "congress_trades.db"))
STATE_FILE = os.path.join(DATA_DIR, "sync_state.json")
ALERTS_FILE = os.path.join(DATA_DIR, "new_trades.json")
PENDING_FILE = os.path.join(DATA_DIR, "pending_congress_alert.txt")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


def init_db():
    """Initialize SQLite database and return connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_key TEXT UNIQUE NOT NULL,
            representative TEXT,
            party TEXT,
            house TEXT,
            ticker TEXT,
            transaction_type TEXT,
            transaction_date TEXT,
            report_date TEXT,
            range_amount TEXT,
            description TEXT,
            raw_json TEXT,
            synced_at TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_trade_key ON trades(trade_key)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ticker ON trades(ticker)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_representative ON trades(representative)")
    conn.commit()
    return conn


def fetch_trades(limit=200):
    """Fetch latest trades from Quiver API."""
    resp = requests.get(
        f"{API_BASE}?limit={limit}",
        headers={
            "Authorization": f"Token {API_KEY}",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; CongressTradesBot/1.0)",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"initialized": False}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def trade_key(t):
    """Unique key for deduplication."""
    return f"{t['Representative']}_{t['TransactionDate']}_{t['Ticker']}_{t['Transaction']}_{t.get('Range', '')}"


def parse_range_lower(range_str):
    """Parse lower bound from range like '$1,001 - $15,000'. Returns 0 on failure."""
    if not range_str:
        return 0
    try:
        lower = range_str.split("-")[0].strip().replace("$", "").replace(",", "")
        return int(lower)
    except (ValueError, IndexError):
        return 0


def is_significant_trade(t):
    """Only report trades above configured threshold."""
    return parse_range_lower(t.get("Range", "")) >= MIN_TRADE_AMOUNT


def format_trade(t):
    """Format a trade for display."""
    txn = t["Transaction"]
    emoji = "🟢" if txn == "Purchase" else "🔴" if txn == "Sale" else "⚪"
    party = f"({t.get('Party', '?')})" if t.get("Party") else ""
    house = t.get("House", "")[:3]
    return (
        f"{emoji} {txn.upper()}: {t['Representative']} {party} [{house}]\n"
        f"   ${t['Ticker']} — {t.get('Range', 'Unknown amount')}\n"
        f"   Trade: {t['TransactionDate']} | Reported: {t['ReportDate']}"
    )


def insert_trade(conn, t):
    """Insert trade into SQLite. Returns True if new (inserted), False if duplicate."""
    key = trade_key(t)
    now = datetime.now(timezone.utc).isoformat()
    try:
        conn.execute(
            """INSERT INTO trades (trade_key, representative, party, house, ticker,
               transaction_type, transaction_date, report_date, range_amount,
               description, raw_json, synced_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                key,
                t.get("Representative"),
                t.get("Party"),
                t.get("House"),
                t.get("Ticker"),
                t.get("Transaction"),
                t.get("TransactionDate"),
                t.get("ReportDate"),
                t.get("Range"),
                t.get("Description"),
                json.dumps(t),
                now,
            ),
        )
        return True
    except sqlite3.IntegrityError:
        return False


def run():
    state = load_state()

    try:
        trades = fetch_trades(limit=200)
    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()[:19]}] API error: {e}")
        return

    if not trades:
        print(f"[{datetime.now(timezone.utc).isoformat()[:19]}] No trades returned")
        return

    conn = init_db()
    first_run = not state["initialized"]
    new_trades = []

    for t in trades:
        if insert_trade(conn, t):
            new_trades.append(t)

    conn.commit()
    now = datetime.now(timezone.utc).isoformat()[:19]
    total = conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]

    if first_run:
        state["initialized"] = True
        state["last_sync"] = now
        state["total_stored"] = total
        save_state(state)

        if trades:
            newest = trades[0]
            alert_msg = f"Congress trades DB initialized. {len(trades)} trades synced.\n\nNewest trade:\n{format_trade(newest)}"
            _write_alert(alert_msg, now, trades=[newest])
            print(f"[{now}] Initial sync: {len(trades)} trades stored.")
    else:
        state["last_sync"] = now
        state["total_stored"] = total
        save_state(state)

        if new_trades:
            buy_sells = [
                t
                for t in new_trades
                if t.get("Transaction") in ("Purchase", "Sale") and is_significant_trade(t)
            ]

            if buy_sells:
                formatted = "\n\n".join(format_trade(t) for t in buy_sells)
                alert_msg = f"🏛️ {len(buy_sells)} new congress trade(s) detected:\n\n{formatted}"
                _write_alert(alert_msg, now, trades=buy_sells)
                print(
                    f"[{now}] {len(buy_sells)} new trades: "
                    + ", ".join(f"{t['Representative']} {t['Transaction']} ${t['Ticker']}" for t in buy_sells)
                )
            else:
                print(f"[{now}] {len(new_trades)} new entries (no significant buy/sell). Total: {total}")
        else:
            print(f"[{now}] No new trades. Total: {total}")

    conn.close()


def _write_alert(message, timestamp, trades=None):
    """Write alert to both history and pending file."""
    alert = {
        "type": "new_trades",
        "message": message,
        "timestamp": timestamp,
        "trades": [
            {
                "politician": t["Representative"],
                "party": t.get("Party"),
                "ticker": t["Ticker"],
                "transaction": t["Transaction"],
                "range": t.get("Range"),
                "date": t["TransactionDate"],
            }
            for t in (trades or [])
        ],
    }

    existing = []
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE) as f:
                existing = json.load(f)
        except Exception:
            pass
    existing.append(alert)
    existing = existing[-50:]
    with open(ALERTS_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    with open(PENDING_FILE, "w") as f:
        f.write(message)


if __name__ == "__main__":
    run()
