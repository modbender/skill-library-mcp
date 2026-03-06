#!/usr/bin/env python3
"""
📊 AI CFO — Full AI Chief Financial Officer
Connects Mercury Banking + Stripe for real-time business intelligence.

Usage: python3 ai_cfo.py <command> [options]

Commands:
  dashboard     Full financial dashboard
  transactions  Recent transactions with AI categorization
  pnl           P&L statement for date range
  cashflow      Cash flow analysis with forecast
  revenue       Stripe revenue breakdown
  expenses      Categorized expenses with trends
  report        Executive financial report
  budget        Set and track budgets
  runway        Burn rate and runway
  invoice       Outstanding invoices and aging
"""

import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, date
from pathlib import Path

# ---------------------------------------------------------------------------
# Langfuse Tracing
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../tools"))
try:
    from lf_trace import trace, trace_api_call, trace_llm_call, flush
    HAS_LANGFUSE = True
except ImportError:
    HAS_LANGFUSE = False
    class _ctx:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def update(self, **kw): pass
        def span(self, *a, **kw): return self
    def trace(*a, **kw): return _ctx()
    def trace_api_call(*a, **kw): pass
    def trace_llm_call(*a, **kw): pass
    def flush(): pass

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MERCURY_BASE = "https://api.mercury.com/api/v1"
STRIPE_BASE = "https://api.stripe.com/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / ".data" / "sqlite"
DB_PATH = DATA_DIR / "cfo.db"

EXPENSE_CATEGORIES = [
    "Revenue", "COGS", "Marketing", "Software/SaaS", "Payroll",
    "Office", "Travel", "Professional Services", "Tax", "Transfer", "Other"
]

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def get_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _init_db(conn)
    return conn

def _init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            account_id TEXT,
            account_name TEXT,
            source TEXT,  -- mercury or stripe
            amount REAL,
            date TEXT,
            description TEXT,
            category TEXT,
            counterparty TEXT,
            raw_json TEXT,
            categorized_at TEXT
        );
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            monthly_limit REAL,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS snapshots (
            date TEXT PRIMARY KEY,
            total_cash REAL,
            checking REAL,
            savings REAL,
            stripe_balance REAL,
            daily_revenue REAL,
            daily_expenses REAL,
            mrr REAL,
            burn_rate REAL,
            runway_months REAL,
            raw_json TEXT
        );
        CREATE TABLE IF NOT EXISTS pnl_monthly (
            month TEXT PRIMARY KEY,
            revenue REAL,
            cogs REAL,
            marketing REAL,
            software REAL,
            payroll REAL,
            office REAL,
            travel REAL,
            professional REAL,
            tax REAL,
            other REAL,
            net_income REAL,
            raw_json TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(date);
        CREATE INDEX IF NOT EXISTS idx_tx_category ON transactions(category);
        CREATE INDEX IF NOT EXISTS idx_tx_source ON transactions(source);
    """)
    conn.commit()

# ---------------------------------------------------------------------------
# API Helpers
# ---------------------------------------------------------------------------
def _env(key):
    val = os.environ.get(key)
    if not val:
        print(f"❌ Missing environment variable: {key}")
        sys.exit(1)
    return val

def _api_get(url, headers, params=None, service="api"):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers["User-Agent"] = "Mozilla/5.0 (compatible; AgxntSix/1.0)"
    req = urllib.request.Request(url, headers=headers, method="GET")
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            ms = int((time.time() - start) * 1000)
            trace_api_call(service, url.split("?")[0].split("/api/")[-1], response_code=200, duration_ms=ms)
            return data
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        ms = int((time.time() - start) * 1000)
        trace_api_call(service, url.split("?")[0].split("/api/")[-1], response_code=e.code, duration_ms=ms, error=body[:200])
        print(f"❌ API error {e.code}: {body[:300]}")
        return None
    except Exception as e:
        trace_api_call(service, url.split("?")[0], response_code=0, error=str(e))
        print(f"❌ Request failed: {e}")
        return None

def mercury_get(path, params=None):
    token = os.environ.get("MERCURY_API_TOKEN", os.environ.get("MERCURY_API_KEY", ""))
    return _api_get(f"{MERCURY_BASE}{path}", {"Authorization": f"Bearer {token}", "Accept": "application/json"}, params, service="mercury")

def stripe_get(path, params=None):
    key = _env("STRIPE_API_KEY")
    return _api_get(f"{STRIPE_BASE}{path}", {"Authorization": f"Bearer {key}", "Accept": "application/json"}, params)

def openrouter_chat(prompt, model="openai/gpt-4o-mini"):
    key = _env("OPENROUTER_API_KEY")
    data = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
        data=data, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            r = json.loads(resp.read().decode())
            return r["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return "Other"

# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------
def fmt_money(amount):
    if amount is None:
        return "$0.00"
    neg = amount < 0
    val = abs(amount)
    s = f"${val:,.2f}"
    return f"-{s}" if neg else s

def fmt_date(d):
    if isinstance(d, str):
        try:
            d = datetime.fromisoformat(d.replace("Z", "+00:00"))
        except:
            return d[:10]
    return d.strftime("%b %d, %Y")

def fmt_pct(val):
    return f"{val:.1f}%"

# ---------------------------------------------------------------------------
# Mercury Operations
# ---------------------------------------------------------------------------
def get_mercury_accounts():
    data = mercury_get("/accounts")
    if not data:
        return []
    return data.get("accounts", data) if isinstance(data, dict) else data

def get_mercury_transactions(account_id, start=None, end=None, limit=500):
    params = {"limit": limit}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    data = mercury_get(f"/account/{account_id}/transactions", params)
    if not data:
        return []
    return data.get("transactions", data) if isinstance(data, dict) else data

def get_all_mercury_transactions(start=None, end=None, limit=500):
    accounts = get_mercury_accounts()
    all_tx = []
    for acc in accounts:
        acc_id = acc.get("id", "")
        acc_name = acc.get("name", acc.get("nickname", "Unknown"))
        txns = get_mercury_transactions(acc_id, start, end, limit)
        for tx in txns:
            tx["_account_id"] = acc_id
            tx["_account_name"] = acc_name
        all_tx.extend(txns)
    all_tx.sort(key=lambda x: x.get("postedDate", x.get("createdAt", "")), reverse=True)
    return all_tx

# ---------------------------------------------------------------------------
# Stripe Operations
# ---------------------------------------------------------------------------
def get_stripe_balance():
    return stripe_get("/balance")

def get_stripe_charges(limit=100, created_gte=None):
    params = {"limit": limit}
    if created_gte:
        params["created[gte]"] = int(datetime.fromisoformat(created_gte).timestamp())
    return stripe_get("/charges", params)

def get_stripe_subscriptions(status="active"):
    return stripe_get("/subscriptions", {"status": status, "limit": 100})

def get_stripe_invoices(status=None, limit=100):
    params = {"limit": limit}
    if status:
        params["status"] = status
    return stripe_get("/invoices", params)

def get_stripe_payouts(limit=50):
    return stripe_get("/payouts", {"limit": limit})

# ---------------------------------------------------------------------------
# AI Categorization
# ---------------------------------------------------------------------------
def categorize_transaction(description, amount, counterparty=""):
    prompt = f"""Categorize this bank transaction into exactly one category.
Categories: {', '.join(EXPENSE_CATEGORIES)}

Transaction:
- Description: {description}
- Amount: ${amount}
- Counterparty: {counterparty}

Rules:
- Incoming money from Stripe/payment processors = Revenue
- Software subscriptions (AWS, Google, Slack, etc.) = Software/SaaS
- Transfers between own accounts = Transfer
- Ad spend (Google Ads, Meta, etc.) = Marketing

Reply with ONLY the category name, nothing else."""
    result = openrouter_chat(prompt)
    for cat in EXPENSE_CATEGORIES:
        if cat.lower() in result.lower():
            return cat
    return "Other"

def categorize_batch(transactions):
    """Categorize transactions, using cache when available."""
    db = get_db()
    results = []
    to_categorize = []

    for tx in transactions:
        tx_id = tx.get("id", tx.get("externalId", ""))
        row = db.execute("SELECT category FROM transactions WHERE id = ?", (tx_id,)).fetchone()
        if row and row["category"]:
            tx["_category"] = row["category"]
            results.append(tx)
        else:
            to_categorize.append(tx)
            results.append(tx)

    for tx in to_categorize:
        desc = tx.get("bankDescription", tx.get("description", ""))
        amount = tx.get("amount", 0)
        cp = tx.get("counterpartyName", tx.get("counterpartyNickname", ""))
        cat = categorize_transaction(desc, amount, cp)
        tx["_category"] = cat
        _store_transaction(db, tx, "mercury", cat)

    db.close()
    return results

def _store_transaction(db, tx, source, category):
    tx_id = tx.get("id", tx.get("externalId", ""))
    if not tx_id:
        return
    db.execute("""INSERT OR REPLACE INTO transactions
        (id, account_id, account_name, source, amount, date, description, category, counterparty, raw_json, categorized_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
        tx_id,
        tx.get("_account_id", ""),
        tx.get("_account_name", ""),
        source,
        tx.get("amount", 0),
        tx.get("postedDate", tx.get("createdAt", ""))[:10],
        tx.get("bankDescription", tx.get("description", "")),
        category,
        tx.get("counterpartyName", tx.get("counterpartyNickname", "")),
        json.dumps(tx),
        datetime.now().isoformat()
    ))
    db.commit()

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_dashboard(args):
    """Full financial dashboard."""
    print("📊 **AI CFO Dashboard**")
    print(f"📅 {fmt_date(datetime.now())}\n")

    # Mercury balances
    accounts = get_mercury_accounts()
    total_cash = 0
    checking = savings = 0
    print("### 🏦 Mercury Banking")
    print("| Account | Balance |")
    print("|---------|---------|")
    for acc in accounts:
        bal = acc.get("currentBalance", acc.get("availableBalance", 0))
        name = acc.get("name", acc.get("nickname", "Unknown"))
        kind = acc.get("kind", acc.get("type", ""))
        total_cash += bal
        if "check" in kind.lower() or "check" in name.lower():
            checking += bal
        elif "sav" in kind.lower() or "sav" in name.lower():
            savings += bal
        print(f"| {name} | {fmt_money(bal)} |")
    print(f"| **Total Cash** | **{fmt_money(total_cash)}** |")
    print()

    # Stripe balance
    stripe_bal_data = get_stripe_balance()
    stripe_available = 0
    stripe_pending = 0
    if stripe_bal_data:
        for b in stripe_bal_data.get("available", []):
            stripe_available += b.get("amount", 0) / 100
        for b in stripe_bal_data.get("pending", []):
            stripe_pending += b.get("amount", 0) / 100
        print("### 💳 Stripe")
        print(f"- Available: {fmt_money(stripe_available)}")
        print(f"- Pending: {fmt_money(stripe_pending)}")
        print()
    elif os.environ.get("STRIPE_API_KEY"):
        print("### 💳 Stripe\n⚠️ Could not fetch Stripe balance\n")
    else:
        print("### 💳 Stripe\n⏳ Stripe API key not configured yet\n")

    # MRR from subscriptions
    mrr = 0
    subs = get_stripe_subscriptions()
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
        print(f"### 📈 Revenue")
        print(f"- MRR: {fmt_money(mrr)}")
        print(f"- ARR: {fmt_money(mrr * 12)}")
        print()

    # Burn rate (last 30 days expenses from Mercury)
    start_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    all_tx = get_all_mercury_transactions(start=start_30)
    total_out = sum(abs(tx.get("amount", 0)) for tx in all_tx if tx.get("amount", 0) < 0)
    total_in = sum(tx.get("amount", 0) for tx in all_tx if tx.get("amount", 0) > 0)
    monthly_burn = total_out
    net_burn = total_out - total_in

    print("### 🔥 Burn Rate (Last 30 Days)")
    print(f"- Gross Burn: {fmt_money(monthly_burn)}")
    print(f"- Revenue In: {fmt_money(total_in)}")
    print(f"- Net Burn: {fmt_money(net_burn)}")
    print()

    # Runway
    if net_burn > 0:
        runway = total_cash / net_burn
        emoji = "🟢" if runway > 12 else "🟡" if runway > 6 else "🔴"
        print(f"### 🛤️ Runway")
        print(f"- {emoji} **{runway:.1f} months** at current net burn")
    elif net_burn <= 0:
        print(f"### 🛤️ Runway")
        print(f"- 🟢 **Profitable!** Net positive cash flow")
    print()

    # Store snapshot
    db = get_db()
    db.execute("""INSERT OR REPLACE INTO snapshots
        (date, total_cash, checking, savings, stripe_balance, daily_revenue, daily_expenses, mrr, burn_rate, runway_months)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
        date.today().isoformat(), total_cash, checking, savings, stripe_available,
        total_in / 30, total_out / 30, mrr, monthly_burn,
        total_cash / net_burn if net_burn > 0 else 999
    ))
    db.commit()
    db.close()


def cmd_transactions(args):
    """Recent transactions with AI categorization."""
    days = args.days or 14
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    limit = args.limit or 50

    print(f"📋 **Recent Transactions** (last {days} days)\n")
    txns = get_all_mercury_transactions(start=start, limit=limit)

    if not txns:
        print("No transactions found.")
        return

    # Categorize
    if not args.skip_categorize:
        txns = categorize_batch(txns)

    print(f"| Date | Description | Amount | Category | Account |")
    print(f"|------|-------------|--------|----------|---------|")
    for tx in txns[:limit]:
        d = tx.get("postedDate", tx.get("createdAt", ""))[:10]
        desc = tx.get("bankDescription", tx.get("description", ""))[:40]
        amt = tx.get("amount", 0)
        cat = tx.get("_category", "—")
        acc = tx.get("_account_name", "")[:15]
        print(f"| {d} | {desc} | {fmt_money(amt)} | {cat} | {acc} |")

    total_in = sum(tx.get("amount", 0) for tx in txns if tx.get("amount", 0) > 0)
    total_out = sum(abs(tx.get("amount", 0)) for tx in txns if tx.get("amount", 0) < 0)
    print(f"\n**Total In:** {fmt_money(total_in)} | **Total Out:** {fmt_money(total_out)} | **Net:** {fmt_money(total_in - total_out)}")


def cmd_pnl(args):
    """Generate P&L statement."""
    end_date = args.end or date.today().isoformat()
    start_date = args.start or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    print(f"📊 **Profit & Loss Statement**")
    print(f"📅 {fmt_date(start_date)} — {fmt_date(end_date)}\n")

    # Revenue from Stripe
    stripe_revenue = 0
    charges = get_stripe_charges(limit=100, created_gte=start_date)
    if charges and charges.get("data"):
        for ch in charges["data"]:
            if ch.get("status") == "succeeded" and not ch.get("refunded"):
                stripe_revenue += ch.get("amount", 0) / 100

    # Expenses from Mercury
    txns = get_all_mercury_transactions(start=start_date, end=end_date)
    if not args.skip_categorize:
        txns = categorize_batch(txns)

    # Also count Mercury inflows as revenue if no Stripe
    mercury_revenue = sum(tx.get("amount", 0) for tx in txns
        if tx.get("amount", 0) > 0 and tx.get("_category") == "Revenue")

    categories = {}
    for tx in txns:
        if tx.get("amount", 0) < 0:
            cat = tx.get("_category", "Other")
            if cat == "Transfer":
                continue
            categories[cat] = categories.get(cat, 0) + abs(tx.get("amount", 0))

    total_revenue = stripe_revenue + mercury_revenue
    cogs = categories.pop("COGS", 0)
    gross_profit = total_revenue - cogs
    total_opex = sum(categories.values())
    net_income = gross_profit - total_opex

    print("### Revenue")
    if stripe_revenue:
        print(f"  Stripe Revenue: {fmt_money(stripe_revenue)}")
    if mercury_revenue:
        print(f"  Other Revenue: {fmt_money(mercury_revenue)}")
    print(f"  **Total Revenue: {fmt_money(total_revenue)}**\n")

    print(f"### Cost of Goods Sold")
    print(f"  COGS: {fmt_money(cogs)}")
    print(f"  **Gross Profit: {fmt_money(gross_profit)}**\n")

    print(f"### Operating Expenses")
    for cat in ["Marketing", "Software/SaaS", "Payroll", "Office", "Travel", "Professional Services", "Tax", "Other"]:
        val = categories.get(cat, 0)
        if val > 0:
            print(f"  {cat}: {fmt_money(val)}")
    print(f"  **Total OpEx: {fmt_money(total_opex)}**\n")

    emoji = "🟢" if net_income >= 0 else "🔴"
    margin = (net_income / total_revenue * 100) if total_revenue else 0
    print(f"### {emoji} Net Income: {fmt_money(net_income)} ({fmt_pct(margin)} margin)")


def cmd_cashflow(args):
    """Cash flow analysis with forecast."""
    print("💰 **Cash Flow Analysis**\n")

    # Get 90 days of data
    start_90 = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    txns = get_all_mercury_transactions(start=start_90)

    if not txns:
        print("No transaction data available.")
        return

    # Aggregate by week
    weekly = {}
    for tx in txns:
        d = tx.get("postedDate", tx.get("createdAt", ""))[:10]
        try:
            dt = datetime.strptime(d, "%Y-%m-%d")
            week_start = dt - timedelta(days=dt.weekday())
            key = week_start.strftime("%Y-%m-%d")
        except:
            continue
        if key not in weekly:
            weekly[key] = {"inflow": 0, "outflow": 0}
        amt = tx.get("amount", 0)
        if amt > 0:
            weekly[key]["inflow"] += amt
        else:
            weekly[key]["outflow"] += abs(amt)

    weeks = sorted(weekly.keys())
    print("### Weekly Cash Flow (Last 90 Days)")
    print("| Week Starting | Inflow | Outflow | Net |")
    print("|--------------|--------|---------|-----|")
    net_flows = []
    for w in weeks:
        inf = weekly[w]["inflow"]
        out = weekly[w]["outflow"]
        net = inf - out
        net_flows.append(net)
        emoji = "🟢" if net >= 0 else "🔴"
        print(f"| {w} | {fmt_money(inf)} | {fmt_money(out)} | {emoji} {fmt_money(net)} |")

    # Linear regression forecast
    if len(net_flows) >= 4:
        n = len(net_flows)
        x_vals = list(range(n))
        x_mean = sum(x_vals) / n
        y_mean = sum(net_flows) / n
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, net_flows))
        den = sum((x - x_mean) ** 2 for x in x_vals)
        slope = num / den if den != 0 else 0
        intercept = y_mean - slope * x_mean

        print(f"\n### 📈 Cash Flow Forecast (Linear Regression)")
        print(f"- Weekly trend: {fmt_money(slope)}/week")
        print(f"| Period | Projected Weekly Net |")
        print(f"|--------|---------------------|")
        for period, weeks_ahead in [("30 days", 4), ("60 days", 9), ("90 days", 13)]:
            projected = intercept + slope * (n + weeks_ahead)
            print(f"| {period} | {fmt_money(projected)} |")

        # Cash position forecast
        accounts = get_mercury_accounts()
        current_cash = sum(acc.get("currentBalance", acc.get("availableBalance", 0)) for acc in accounts)
        avg_weekly = sum(net_flows) / len(net_flows)
        print(f"\n### 💵 Projected Cash Position")
        print(f"- Current: {fmt_money(current_cash)}")
        for label, wks in [("30 days", 4), ("60 days", 9), ("90 days", 13)]:
            proj = current_cash + avg_weekly * wks
            print(f"- {label}: {fmt_money(proj)}")


def cmd_revenue(args):
    """Stripe revenue breakdown."""
    print("💰 **Revenue Analysis**\n")

    if not os.environ.get("STRIPE_API_KEY"):
        print("⏳ Stripe API key not configured yet. Revenue analysis will be available once connected.")
        return

    # MRR from subscriptions
    subs = get_stripe_subscriptions()
    mrr = 0
    active_count = 0
    if subs and subs.get("data"):
        active_count = len(subs["data"])
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

    print(f"### Subscription Metrics")
    print(f"- Active Subscriptions: {active_count}")
    print(f"- MRR: {fmt_money(mrr)}")
    print(f"- ARR: {fmt_money(mrr * 12)}")
    print()

    # Recent charges
    start_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    charges = get_stripe_charges(limit=100, created_gte=start_30)
    if charges and charges.get("data"):
        succeeded = [c for c in charges["data"] if c.get("status") == "succeeded"]
        total_30 = sum(c.get("amount", 0) / 100 for c in succeeded)
        refunded = sum(c.get("amount_refunded", 0) / 100 for c in charges["data"])
        print(f"### Last 30 Days")
        print(f"- Gross Revenue: {fmt_money(total_30)}")
        print(f"- Refunds: {fmt_money(refunded)}")
        print(f"- Net Revenue: {fmt_money(total_30 - refunded)}")
        print(f"- Transactions: {len(succeeded)}")
        if succeeded:
            avg = total_30 / len(succeeded)
            print(f"- Avg Transaction: {fmt_money(avg)}")
    print()

    # Payouts
    payouts = get_stripe_payouts()
    if payouts and payouts.get("data"):
        recent = payouts["data"][:5]
        print("### Recent Payouts")
        print("| Date | Amount | Status |")
        print("|------|--------|--------|")
        for p in recent:
            d = datetime.fromtimestamp(p.get("arrival_date", 0)).strftime("%Y-%m-%d") if p.get("arrival_date") else "—"
            print(f"| {d} | {fmt_money(p.get('amount', 0) / 100)} | {p.get('status', '—')} |")


def cmd_expenses(args):
    """Categorized expenses with trends."""
    days = args.days or 30
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    print(f"💸 **Expense Analysis** (last {days} days)\n")

    txns = get_all_mercury_transactions(start=start)
    expenses = [tx for tx in txns if tx.get("amount", 0) < 0]

    if not expenses:
        print("No expenses found.")
        return

    if not args.skip_categorize:
        expenses = categorize_batch(expenses)

    # Group by category
    by_cat = {}
    for tx in expenses:
        cat = tx.get("_category", "Other")
        if cat == "Transfer":
            continue
        if cat not in by_cat:
            by_cat[cat] = {"total": 0, "count": 0, "items": []}
        by_cat[cat]["total"] += abs(tx.get("amount", 0))
        by_cat[cat]["count"] += 1
        by_cat[cat]["items"].append(tx)

    total = sum(v["total"] for v in by_cat.values())

    print("### Expense Breakdown")
    print("| Category | Amount | % | Count |")
    print("|----------|--------|---|-------|")
    for cat, data in sorted(by_cat.items(), key=lambda x: -x[1]["total"]):
        pct = (data["total"] / total * 100) if total else 0
        print(f"| {cat} | {fmt_money(data['total'])} | {fmt_pct(pct)} | {data['count']} |")
    print(f"| **Total** | **{fmt_money(total)}** | **100%** | **{sum(v['count'] for v in by_cat.values())}** |")

    # Top expenses
    print(f"\n### Top 10 Expenses")
    print("| Date | Description | Amount | Category |")
    print("|------|-------------|--------|----------|")
    sorted_exp = sorted(expenses, key=lambda x: x.get("amount", 0))[:10]
    for tx in sorted_exp:
        d = tx.get("postedDate", tx.get("createdAt", ""))[:10]
        desc = tx.get("bankDescription", tx.get("description", ""))[:40]
        print(f"| {d} | {desc} | {fmt_money(abs(tx.get('amount', 0)))} | {tx.get('_category', '—')} |")

    # Anomaly detection: flag items >2x category average
    print(f"\n### ⚠️ Anomalies (>2x category average)")
    found = False
    for cat, data in by_cat.items():
        if data["count"] < 2:
            continue
        avg = data["total"] / data["count"]
        for tx in data["items"]:
            amt = abs(tx.get("amount", 0))
            if amt > avg * 2:
                desc = tx.get("bankDescription", tx.get("description", ""))[:40]
                print(f"- **{desc}**: {fmt_money(amt)} (avg in {cat}: {fmt_money(avg)})")
                found = True
    if not found:
        print("None detected ✅")


def cmd_report(args):
    """Executive financial report."""
    period = args.period or "weekly"
    if period == "weekly":
        days = 7
        start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        label = f"Week of {fmt_date(datetime.now() - timedelta(days=7))}"
    else:
        days = 30
        start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        label = datetime.now().strftime("%B %Y")

    print(f"📊 **Executive Financial Report**")
    print(f"📅 {label}\n")
    print("---\n")

    # Cash position
    accounts = get_mercury_accounts()
    total_cash = sum(acc.get("currentBalance", acc.get("availableBalance", 0)) for acc in accounts)
    print(f"### 💵 Cash Position: {fmt_money(total_cash)}")
    for acc in accounts:
        name = acc.get("name", acc.get("nickname", ""))
        bal = acc.get("currentBalance", acc.get("availableBalance", 0))
        print(f"- {name}: {fmt_money(bal)}")
    print()

    # Period activity
    txns = get_all_mercury_transactions(start=start)
    inflow = sum(tx.get("amount", 0) for tx in txns if tx.get("amount", 0) > 0)
    outflow = sum(abs(tx.get("amount", 0)) for tx in txns if tx.get("amount", 0) < 0)

    print(f"### 📈 {period.title()} Activity")
    print(f"- Money In: {fmt_money(inflow)}")
    print(f"- Money Out: {fmt_money(outflow)}")
    print(f"- Net: {fmt_money(inflow - outflow)}")
    print()

    # Stripe summary
    if os.environ.get("STRIPE_API_KEY"):
        charges = get_stripe_charges(limit=100, created_gte=start)
        if charges and charges.get("data"):
            rev = sum(c.get("amount", 0) / 100 for c in charges["data"] if c.get("status") == "succeeded")
            print(f"### 💳 Stripe Revenue: {fmt_money(rev)}")
            print()

    # Burn rate and runway
    monthly_out = outflow * (30 / days)
    monthly_in = inflow * (30 / days)
    net_burn = monthly_out - monthly_in
    if net_burn > 0:
        runway = total_cash / net_burn
        emoji = "🟢" if runway > 12 else "🟡" if runway > 6 else "🔴"
        print(f"### 🛤️ Runway: {emoji} {runway:.1f} months")
    else:
        print(f"### 🛤️ Runway: 🟢 Profitable (net positive)")
    print()

    print("---")
    print(f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} by AI CFO*")


def cmd_budget(args):
    """Set and track budgets."""
    db = get_db()

    if args.set_category and args.set_amount:
        db.execute("INSERT OR REPLACE INTO budgets (category, monthly_limit, updated_at) VALUES (?, ?, ?)",
            (args.set_category, args.set_amount, datetime.now().isoformat()))
        db.commit()
        print(f"✅ Budget set: {args.set_category} = {fmt_money(args.set_amount)}/month")
        db.close()
        return

    # Show budget vs actual
    print("📋 **Budget Tracking**\n")
    month_start = date.today().replace(day=1).isoformat()
    budgets = db.execute("SELECT * FROM budgets ORDER BY category").fetchall()

    if not budgets:
        print("No budgets set. Use `--set <category> <amount>` to create one.")
        print(f"\nExample: `python3 ai_cfo.py budget --set Marketing 5000`")
        db.close()
        return

    # Get this month's actuals
    actuals = db.execute("""
        SELECT category, SUM(ABS(amount)) as total
        FROM transactions
        WHERE date >= ? AND amount < 0
        GROUP BY category
    """, (month_start,)).fetchall()
    actual_map = {r["category"]: r["total"] for r in actuals}

    print(f"### {date.today().strftime('%B %Y')}")
    print("| Category | Budget | Actual | Remaining | Status |")
    print("|----------|--------|--------|-----------|--------|")
    for b in budgets:
        cat = b["category"]
        limit = b["monthly_limit"]
        actual = actual_map.get(cat, 0)
        remaining = limit - actual
        pct = (actual / limit * 100) if limit else 0
        if pct >= 100:
            status = "🔴 OVER"
        elif pct >= 80:
            status = "🟡 WARNING"
        else:
            status = "🟢 OK"
        print(f"| {cat} | {fmt_money(limit)} | {fmt_money(actual)} | {fmt_money(remaining)} | {status} ({fmt_pct(pct)}) |")

    db.close()


def cmd_runway(args):
    """Calculate burn rate and runway."""
    print("🛤️ **Burn Rate & Runway Analysis**\n")

    accounts = get_mercury_accounts()
    total_cash = sum(acc.get("currentBalance", acc.get("availableBalance", 0)) for acc in accounts)

    # Last 3 months data
    for months, label in [(1, "Last 30 Days"), (3, "Last 90 Days")]:
        start = (datetime.now() - timedelta(days=months * 30)).strftime("%Y-%m-%d")
        txns = get_all_mercury_transactions(start=start)
        outflow = sum(abs(tx.get("amount", 0)) for tx in txns if tx.get("amount", 0) < 0)
        inflow = sum(tx.get("amount", 0) for tx in txns if tx.get("amount", 0) > 0)
        monthly_out = outflow / months
        monthly_in = inflow / months
        net_burn = monthly_out - monthly_in

        print(f"### {label}")
        print(f"- Monthly Gross Burn: {fmt_money(monthly_out)}")
        print(f"- Monthly Revenue: {fmt_money(monthly_in)}")
        print(f"- Monthly Net Burn: {fmt_money(net_burn)}")
        if net_burn > 0:
            runway = total_cash / net_burn
            emoji = "🟢" if runway > 12 else "🟡" if runway > 6 else "🔴"
            print(f"- Runway: {emoji} **{runway:.1f} months**")
        else:
            print(f"- Runway: 🟢 **Profitable!**")
        print()

    print(f"### 💵 Total Cash: {fmt_money(total_cash)}")


def cmd_invoice(args):
    """List outstanding Stripe invoices."""
    print("🧾 **Outstanding Invoices**\n")

    if not os.environ.get("STRIPE_API_KEY"):
        print("⏳ Stripe API key not configured yet.")
        return

    invoices = get_stripe_invoices(status="open")
    if not invoices or not invoices.get("data"):
        print("No outstanding invoices. ✅")
        return

    total_due = 0
    print("| Invoice | Customer | Amount Due | Created | Days Outstanding |")
    print("|---------|----------|-----------|---------|-----------------|")
    for inv in invoices["data"]:
        inv_id = inv.get("number", inv.get("id", ""))[:20]
        cust = inv.get("customer_name", inv.get("customer_email", inv.get("customer", "")))[:25]
        amount = inv.get("amount_due", 0) / 100
        total_due += amount
        created = datetime.fromtimestamp(inv.get("created", 0))
        days = (datetime.now() - created).days
        aging = "🟢" if days < 30 else "🟡" if days < 60 else "🔴"
        print(f"| {inv_id} | {cust} | {fmt_money(amount)} | {created.strftime('%Y-%m-%d')} | {aging} {days}d |")

    print(f"\n**Total Outstanding: {fmt_money(total_due)}**")

    # Aging summary
    all_inv = invoices["data"]
    under_30 = sum(i.get("amount_due", 0) / 100 for i in all_inv if (datetime.now() - datetime.fromtimestamp(i.get("created", 0))).days < 30)
    d30_60 = sum(i.get("amount_due", 0) / 100 for i in all_inv if 30 <= (datetime.now() - datetime.fromtimestamp(i.get("created", 0))).days < 60)
    over_60 = sum(i.get("amount_due", 0) / 100 for i in all_inv if (datetime.now() - datetime.fromtimestamp(i.get("created", 0))).days >= 60)

    print(f"\n### Aging Summary")
    print(f"- 0-30 days: {fmt_money(under_30)}")
    print(f"- 30-60 days: {fmt_money(d30_60)}")
    print(f"- 60+ days: {fmt_money(over_60)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="📊 AI CFO — Financial Intelligence", formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # dashboard
    sub.add_parser("dashboard", help="Full financial dashboard")

    # transactions
    p = sub.add_parser("transactions", help="Recent transactions")
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--skip-categorize", action="store_true")

    # pnl
    p = sub.add_parser("pnl", help="P&L statement")
    p.add_argument("--start", type=str)
    p.add_argument("--end", type=str)
    p.add_argument("--skip-categorize", action="store_true")

    # cashflow
    sub.add_parser("cashflow", help="Cash flow analysis")

    # revenue
    sub.add_parser("revenue", help="Revenue breakdown")

    # expenses
    p = sub.add_parser("expenses", help="Categorized expenses")
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--skip-categorize", action="store_true")

    # report
    p = sub.add_parser("report", help="Executive report")
    p.add_argument("--period", choices=["weekly", "monthly"], default="weekly")

    # budget
    p = sub.add_parser("budget", help="Budget tracking")
    p.add_argument("--set", nargs=2, metavar=("CATEGORY", "AMOUNT"), dest="set_pair")

    # runway
    sub.add_parser("runway", help="Burn rate & runway")

    # invoice
    sub.add_parser("invoice", help="Outstanding invoices")

    args = parser.parse_args()

    # Handle budget --set
    if args.command == "budget" and args.set_pair:
        args.set_category = args.set_pair[0]
        args.set_amount = float(args.set_pair[1])
    elif args.command == "budget":
        args.set_category = None
        args.set_amount = None

    commands = {
        "dashboard": cmd_dashboard,
        "transactions": cmd_transactions,
        "pnl": cmd_pnl,
        "cashflow": cmd_cashflow,
        "revenue": cmd_revenue,
        "expenses": cmd_expenses,
        "report": cmd_report,
        "budget": cmd_budget,
        "runway": cmd_runway,
        "invoice": cmd_invoice,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

    flush()
