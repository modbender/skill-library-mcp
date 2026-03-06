#!/usr/bin/env python3
"""Cost Tracker — AI spending monitor for OpenRouter with budget alerts and savings recommendations."""

import argparse
import csv
import io
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install: pip install requests")
    sys.exit(1)

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
BASE_URL = "https://openrouter.ai/api/v1"
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "cost_tracker.db"

# Model tier mapping for savings recommendations
MODEL_TIERS = {
    "premium": ["anthropic/claude-opus-4", "openai/o1", "google/gemini-2.0-ultra"],
    "standard": ["anthropic/claude-sonnet-4", "openai/gpt-4o", "google/gemini-2.0-pro"],
    "budget": ["anthropic/claude-haiku-4.5", "openai/gpt-4o-mini", "google/gemini-2.0-flash-001"],
    "economy": ["meta-llama/llama-3.1-8b-instruct", "mistralai/mistral-7b-instruct"],
}

DOWNGRADE_MAP = {
    "anthropic/claude-opus-4": "anthropic/claude-sonnet-4",
    "openai/o1": "openai/gpt-4o",
    "anthropic/claude-sonnet-4": "anthropic/claude-haiku-4.5",
    "openai/gpt-4o": "openai/gpt-4o-mini",
    "google/gemini-2.0-pro": "google/gemini-2.0-flash-001",
}


def ensure_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usage_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        total_credits REAL DEFAULT 0,
        usage_credits REAL DEFAULT 0,
        remaining_credits REAL DEFAULT 0,
        raw_json TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS model_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        model TEXT NOT NULL,
        prompt_tokens INTEGER DEFAULT 0,
        completion_tokens INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        cost_usd REAL DEFAULT 0.0,
        num_requests INTEGER DEFAULT 1
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS budget_config (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        monthly_limit REAL DEFAULT 0.0,
        alert_threshold REAL DEFAULT 0.8,
        updated_at TEXT
    )""")
    conn.commit()
    conn.close()


def headers():
    return {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def fetch_key_info():
    """Fetch account info from OpenRouter."""
    resp = requests.get(f"{BASE_URL}/auth/key", headers=headers(), timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", {})


def fetch_models():
    resp = requests.get(f"{BASE_URL}/models", headers=headers(), timeout=30)
    resp.raise_for_status()
    return {m["id"]: m for m in resp.json().get("data", [])}


def cmd_fetch(args):
    """Fetch current usage from OpenRouter and store it."""
    ensure_db()
    info = fetch_key_info()
    now = datetime.utcnow().isoformat()

    usage = info.get("usage", 0)
    limit = info.get("limit", 0)
    remaining = (limit - usage) if limit else 0

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO usage_snapshots (timestamp, total_credits, usage_credits, remaining_credits, raw_json) VALUES (?,?,?,?,?)",
        (now, limit, usage, remaining, json.dumps(info)),
    )
    conn.commit()
    conn.close()

    print(f"💰 OpenRouter Usage (fetched {now[:19]})")
    print(f"   Credits used:      ${usage:.4f}")
    if limit:
        print(f"   Credit limit:      ${limit:.4f}")
        print(f"   Remaining:         ${remaining:.4f}")
        pct = (usage / limit * 100) if limit > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"   [{bar}] {pct:.1f}%")
    else:
        print(f"   Credit limit:      unlimited")
    print(f"\n   ✅ Snapshot saved to database")


def cmd_report(args):
    """Show spending report for a period."""
    ensure_db()
    conn = sqlite3.connect(str(DB_PATH))
    now = datetime.utcnow()

    if args.period == "daily":
        since = (now - timedelta(days=1)).isoformat()
        label = "Last 24 Hours"
    elif args.period == "weekly":
        since = (now - timedelta(days=7)).isoformat()
        label = "Last 7 Days"
    else:
        since = (now - timedelta(days=30)).isoformat()
        label = "Last 30 Days"

    # Get snapshots in range
    snapshots = conn.execute(
        "SELECT timestamp, usage_credits FROM usage_snapshots WHERE timestamp >= ? ORDER BY timestamp",
        (since,),
    ).fetchall()

    # Get model usage in range
    model_rows = conn.execute(
        "SELECT model, SUM(num_requests), SUM(prompt_tokens), SUM(completion_tokens), SUM(cost_usd) "
        "FROM model_usage WHERE timestamp >= ? GROUP BY model ORDER BY SUM(cost_usd) DESC",
        (since,),
    ).fetchall()
    conn.close()

    print(f"💰 Cost Report — {label}")
    print("═" * 55)

    if snapshots:
        first_usage = snapshots[0][1]
        last_usage = snapshots[-1][1]
        delta = last_usage - first_usage
        print(f"   Period spend (from snapshots): ${delta:.4f}")
        print(f"   Snapshots collected: {len(snapshots)}")
    else:
        print("   No snapshots in this period. Run 'fetch' to collect data.")

    if model_rows:
        print(f"\n   Per-Model Breakdown:")
        print(f"   {'Model':<40} {'Calls':>6} {'Cost':>10}")
        print(f"   {'─'*56}")
        total = 0
        for model, calls, pt, ct, cost in model_rows:
            print(f"   {model:<40} {calls:>6} ${cost:>9.4f}")
            total += cost
        print(f"   {'─'*56}")
        print(f"   {'TOTAL':<40} {'':>6} ${total:>9.4f}")

    print()


def cmd_models(args):
    """Show per-model spending breakdown."""
    ensure_db()
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT model, SUM(num_requests), SUM(prompt_tokens), SUM(completion_tokens), SUM(cost_usd), "
        "MIN(timestamp), MAX(timestamp) FROM model_usage GROUP BY model ORDER BY SUM(cost_usd) DESC"
    ).fetchall()
    conn.close()

    if not rows:
        print("No model usage data yet. Log some API calls first.")
        return

    print("📊 Per-Model Spending (All Time)")
    print("═" * 70)
    print(f"{'Model':<40} {'Calls':>6} {'Tokens':>10} {'Cost':>10}")
    print("─" * 70)
    for model, calls, pt, ct, cost, first, last in rows:
        tokens = (pt or 0) + (ct or 0)
        print(f"{model:<40} {calls:>6} {tokens:>10,} ${cost:>9.4f}")
    print()


def cmd_budget(args):
    """Set or check budget."""
    ensure_db()
    conn = sqlite3.connect(str(DB_PATH))

    if args.set is not None:
        conn.execute(
            "INSERT OR REPLACE INTO budget_config (id, monthly_limit, alert_threshold, updated_at) VALUES (1, ?, 0.8, ?)",
            (args.set, datetime.utcnow().isoformat()),
        )
        conn.commit()
        print(f"✅ Monthly budget set to ${args.set:.2f}")

    # Always show current status
    row = conn.execute("SELECT monthly_limit, alert_threshold FROM budget_config WHERE id=1").fetchone()
    if not row or row[0] == 0:
        print("No budget configured. Use --set <amount>")
        conn.close()
        return

    limit, threshold = row
    # Get current month spend from snapshots
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0).isoformat()
    snapshots = conn.execute(
        "SELECT usage_credits FROM usage_snapshots WHERE timestamp >= ? ORDER BY timestamp",
        (month_start,),
    ).fetchall()

    spent = 0
    if len(snapshots) >= 2:
        spent = snapshots[-1][0] - snapshots[0][0]
    elif len(snapshots) == 1:
        # Try to get last month's final snapshot
        last = conn.execute(
            "SELECT usage_credits FROM usage_snapshots WHERE timestamp < ? ORDER BY timestamp DESC LIMIT 1",
            (month_start,),
        ).fetchone()
        if last:
            spent = snapshots[0][0] - last[0]

    # Also add model_usage for this month
    model_cost = conn.execute(
        "SELECT COALESCE(SUM(cost_usd), 0) FROM model_usage WHERE timestamp >= ?",
        (month_start,),
    ).fetchone()[0]
    spent = max(spent, model_cost)

    conn.close()
    pct = (spent / limit * 100) if limit > 0 else 0
    status = "🟢" if pct < threshold * 100 else "🟡" if pct < 100 else "🔴"
    bar = "█" * int(min(pct, 100) / 5) + "░" * (20 - int(min(pct, 100) / 5))
    print(f"\n{status} Monthly Budget: ${spent:.4f} / ${limit:.2f}")
    print(f"   [{bar}] {pct:.1f}%")
    if pct >= threshold * 100:
        print(f"   ⚠️ ALERT: Spending at {pct:.1f}% of monthly limit!")
    days_left = (datetime.utcnow().replace(day=28) - datetime.utcnow()).days
    if days_left > 0 and spent > 0:
        projected = spent / max(datetime.utcnow().day, 1) * 30
        print(f"   📈 Projected monthly: ${projected:.2f}")


def cmd_savings(args):
    """Recommend savings opportunities."""
    ensure_db()
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT model, SUM(num_requests), SUM(cost_usd) FROM model_usage GROUP BY model ORDER BY SUM(cost_usd) DESC"
    ).fetchall()
    conn.close()

    if not rows:
        print("No usage data yet. Start tracking to get savings recommendations.")
        return

    models_data = fetch_models()

    print("💡 Savings Recommendations")
    print("═" * 55)
    total_savings = 0

    for model, calls, cost in rows:
        if cost < 0.01:
            continue
        downgrade = DOWNGRADE_MAP.get(model)
        if not downgrade:
            continue

        current_info = models_data.get(model, {})
        alt_info = models_data.get(downgrade, {})
        if not current_info or not alt_info:
            continue

        cur_price = float(current_info.get("pricing", {}).get("prompt", "0")) + float(current_info.get("pricing", {}).get("completion", "0"))
        alt_price = float(alt_info.get("pricing", {}).get("prompt", "0")) + float(alt_info.get("pricing", {}).get("completion", "0"))

        if alt_price < cur_price and cur_price > 0:
            ratio = alt_price / cur_price
            potential = cost * (1 - ratio)
            total_savings += potential
            print(f"\n  {model} → {downgrade}")
            print(f"    Current spend: ${cost:.4f} ({calls} calls)")
            print(f"    Potential savings: ${potential:.4f} ({(1-ratio)*100:.0f}% cheaper)")
            print(f"    Trade-off: Slightly less capable, much cheaper")

    if total_savings > 0:
        print(f"\n  💰 Total potential savings: ${total_savings:.4f}/period")
    else:
        print("  ✅ Already using cost-effective models!")


def cmd_export(args):
    """Export data as JSON or CSV."""
    ensure_db()
    conn = sqlite3.connect(str(DB_PATH))

    snapshots = conn.execute("SELECT timestamp, total_credits, usage_credits, remaining_credits FROM usage_snapshots ORDER BY timestamp").fetchall()
    model_rows = conn.execute("SELECT timestamp, model, prompt_tokens, completion_tokens, cost_usd, num_requests FROM model_usage ORDER BY timestamp").fetchall()
    conn.close()

    if args.format == "json":
        data = {
            "exported_at": datetime.utcnow().isoformat(),
            "snapshots": [{"timestamp": r[0], "total": r[1], "used": r[2], "remaining": r[3]} for r in snapshots],
            "model_usage": [{"timestamp": r[0], "model": r[1], "prompt_tokens": r[2], "completion_tokens": r[3], "cost": r[4], "requests": r[5]} for r in model_rows],
        }
        print(json.dumps(data, indent=2))
    else:
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["timestamp", "model", "prompt_tokens", "completion_tokens", "cost_usd", "num_requests"])
        for r in model_rows:
            writer.writerow(r)
        print(out.getvalue())


def main():
    if not API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Cost Tracker — AI spending monitor")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("fetch", help="Fetch current usage from OpenRouter")

    r = sub.add_parser("report", help="Spending report")
    r.add_argument("--period", default="monthly", choices=["daily", "weekly", "monthly"])

    sub.add_parser("models", help="Per-model breakdown")

    b = sub.add_parser("budget", help="Budget management")
    b.add_argument("--set", type=float, default=None)
    b.add_argument("--check", action="store_true")

    sub.add_parser("savings", help="Savings recommendations")

    e = sub.add_parser("export", help="Export data")
    e.add_argument("--format", default="json", choices=["json", "csv"])

    args = parser.parse_args()
    cmds = {"fetch": cmd_fetch, "report": cmd_report, "models": cmd_models, "budget": cmd_budget, "savings": cmd_savings, "export": cmd_export}
    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
