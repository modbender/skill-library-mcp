#!/usr/bin/env python3
"""
📊 AI CFO Daily Cron — Generates daily financial brief for Telegram.

Run daily at 8 AM:
  python3 cfo_cron.py

Output: Plain text daily brief (cash position, revenue, alerts).
Stores daily snapshot in SQLite.
"""

import json
import os
import sqlite3
import sys
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, date
from pathlib import Path

MERCURY_BASE = "https://api.mercury.com/api/v1"
STRIPE_BASE = "https://api.stripe.com/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / ".data" / "sqlite"
DB_PATH = DATA_DIR / "cfo.db"

def _env(key):
    return os.environ.get(key, "")

def _api_get(url, headers, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except:
        return None

def mercury_get(path, params=None):
    token = _env("MERCURY_API_TOKEN")
    if not token:
        return None
    return _api_get(f"{MERCURY_BASE}{path}", {"Authorization": f"Bearer {token}", "Accept": "application/json"}, params)

def stripe_get(path, params=None):
    key = _env("STRIPE_API_KEY")
    if not key:
        return None
    return _api_get(f"{STRIPE_BASE}{path}", {"Authorization": f"Bearer {key}", "Accept": "application/json"}, params)

def fmt_money(amount):
    if amount is None:
        return "$0.00"
    neg = amount < 0
    s = f"${abs(amount):,.2f}"
    return f"-{s}" if neg else s

def get_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS snapshots (
        date TEXT PRIMARY KEY, total_cash REAL, checking REAL, savings REAL,
        stripe_balance REAL, daily_revenue REAL, daily_expenses REAL,
        mrr REAL, burn_rate REAL, runway_months REAL, raw_json TEXT
    )""")
    conn.commit()
    return conn

def main():
    alerts = []
    lines = []

    # Mercury balances
    accounts_data = mercury_get("/accounts")
    accounts = []
    if accounts_data:
        accounts = accounts_data.get("accounts", accounts_data) if isinstance(accounts_data, dict) else accounts_data

    total_cash = 0
    checking = savings = 0
    for acc in accounts:
        bal = acc.get("currentBalance", acc.get("availableBalance", 0))
        name = acc.get("name", acc.get("nickname", ""))
        kind = acc.get("kind", acc.get("type", ""))
        total_cash += bal
        if "check" in kind.lower() or "check" in name.lower():
            checking += bal
        elif "sav" in kind.lower() or "sav" in name.lower():
            savings += bal

    lines.append(f"💵 Cash: {fmt_money(total_cash)}")

    # Yesterday's activity
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = date.today().isoformat()
    day_in = day_out = 0

    for acc in accounts:
        acc_id = acc.get("id", "")
        txns_data = mercury_get(f"/account/{acc_id}/transactions", {"start": yesterday, "end": today, "limit": 200})
        txns = []
        if txns_data:
            txns = txns_data.get("transactions", txns_data) if isinstance(txns_data, dict) else txns_data
        for tx in txns:
            amt = tx.get("amount", 0)
            if amt > 0:
                day_in += amt
            else:
                day_out += abs(amt)

    if day_in or day_out:
        lines.append(f"📈 Yesterday: +{fmt_money(day_in)} / -{fmt_money(day_out)}")

    # Stripe daily revenue
    stripe_rev = 0
    stripe_key = _env("STRIPE_API_KEY")
    if stripe_key:
        ts = int(datetime.strptime(yesterday, "%Y-%m-%d").timestamp())
        charges = stripe_get("/charges", {"limit": 100, "created[gte]": ts})
        if charges and charges.get("data"):
            stripe_rev = sum(c.get("amount", 0) / 100 for c in charges["data"] if c.get("status") == "succeeded")
            if stripe_rev:
                lines.append(f"💳 Stripe: {fmt_money(stripe_rev)}")

    # MRR
    mrr = 0
    subs = stripe_get("/subscriptions", {"status": "active", "limit": 100}) if stripe_key else None
    if subs and subs.get("data"):
        for sub in subs["data"]:
            for item in sub.get("items", {}).get("data", []):
                price = item.get("price", {})
                amount = price.get("unit_amount", 0) / 100
                interval = price.get("recurring", {}).get("interval", "month")
                qty = item.get("quantity", 1)
                if interval == "year":
                    amount /= 12
                elif interval == "week":
                    amount *= 4.33
                mrr += amount * qty

    # Burn rate (30 day)
    start_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    monthly_out = 0
    monthly_in = 0
    for acc in accounts:
        acc_id = acc.get("id", "")
        txns_data = mercury_get(f"/account/{acc_id}/transactions", {"start": start_30, "limit": 500})
        txns = []
        if txns_data:
            txns = txns_data.get("transactions", txns_data) if isinstance(txns_data, dict) else txns_data
        for tx in txns:
            amt = tx.get("amount", 0)
            if amt > 0:
                monthly_in += amt
            else:
                monthly_out += abs(amt)

    net_burn = monthly_out - monthly_in

    # Runway
    if net_burn > 0:
        runway = total_cash / net_burn
        if runway < 6:
            alerts.append(f"🔴 Runway: {runway:.1f} months — critically low!")
        elif runway < 12:
            alerts.append(f"🟡 Runway: {runway:.1f} months")

    # Budget alerts
    db = get_db()
    month_start = date.today().replace(day=1).isoformat()
    try:
        budgets = db.execute("SELECT * FROM budgets").fetchall()
        for b in budgets:
            actual = db.execute(
                "SELECT SUM(ABS(amount)) as total FROM transactions WHERE category = ? AND date >= ? AND amount < 0",
                (b["category"], month_start)
            ).fetchone()
            if actual and actual["total"]:
                pct = actual["total"] / b["monthly_limit"] * 100
                if pct >= 100:
                    alerts.append(f"🔴 {b['category']} budget exceeded: {fmt_money(actual['total'])} / {fmt_money(b['monthly_limit'])}")
                elif pct >= 80:
                    alerts.append(f"🟡 {b['category']} budget at {pct:.0f}%: {fmt_money(actual['total'])} / {fmt_money(b['monthly_limit'])}")
    except:
        pass

    # Store snapshot
    db.execute("""INSERT OR REPLACE INTO snapshots
        (date, total_cash, checking, savings, stripe_balance, daily_revenue, daily_expenses, mrr, burn_rate, runway_months)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
        today, total_cash, checking, savings, stripe_rev,
        day_in + stripe_rev, day_out, mrr, monthly_out,
        total_cash / net_burn if net_burn > 0 else 999
    ))
    db.commit()
    db.close()

    # Build output
    output = f"📊 Daily CFO Brief — {datetime.now().strftime('%b %d, %Y')}\n"
    output += "\n".join(lines)
    if alerts:
        output += "\n\n⚠️ Alerts:\n" + "\n".join(alerts)
    else:
        output += "\n✅ No alerts"

    print(output)

if __name__ == "__main__":
    main()
