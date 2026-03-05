#!/usr/bin/env python3
"""
cost-guardian — AI & Infrastructure Cost Tracker
Tracks, analyzes, and optimizes total cost of running AI agents and infrastructure.
Zero external dependencies — pure Python 3 stdlib.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import glob

# ─── Constants ────────────────────────────────────────────────────────────────

VERSION = "1.0.0"
DATA_DIR = Path(os.environ.get("COST_GUARDIAN_DIR", 
    os.path.expanduser("~/.openclaw/workspace/costs")))
DB_PATH = DATA_DIR / "costs.db"
CONFIG_PATH = DATA_DIR / "config.json"

# Known model pricing (USD per 1M tokens) — updated Feb 2026
MODEL_PRICING = {
    # OpenAI
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4": {"input": 30.00, "output": 60.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "o1": {"input": 15.00, "output": 60.00},
    "o1-mini": {"input": 3.00, "output": 12.00},
    "o3-mini": {"input": 1.10, "output": 4.40},
    # Anthropic
    "claude-opus-4-6": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku": {"input": 0.80, "output": 4.00},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    "claude-3-opus": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
    # Groq (free/very cheap)
    "llama-3.1-70b-versatile": {"input": 0.59, "output": 0.79},
    "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
    "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
    "mixtral-8x7b-32768": {"input": 0.24, "output": 0.24},
    "gemma2-9b-it": {"input": 0.20, "output": 0.20},
    # OpenRouter passthrough (common)
    "openrouter/auto": {"input": 1.00, "output": 3.00},  # rough estimate
    # Local (Ollama) — free
    "ollama/*": {"input": 0.00, "output": 0.00},
}

CATEGORIES = ["api", "hosting", "power", "subscription", "hardware", "other"]
PERIODS = ["once", "daily", "weekly", "monthly", "yearly"]

# ─── Colors ───────────────────────────────────────────────────────────────────

class C:
    """ANSI color codes (disabled if NO_COLOR or non-TTY)."""
    _enabled = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    
    RESET = "\033[0m" if _enabled else ""
    BOLD = "\033[1m" if _enabled else ""
    DIM = "\033[2m" if _enabled else ""
    RED = "\033[31m" if _enabled else ""
    GREEN = "\033[32m" if _enabled else ""
    YELLOW = "\033[33m" if _enabled else ""
    BLUE = "\033[34m" if _enabled else ""
    MAGENTA = "\033[35m" if _enabled else ""
    CYAN = "\033[36m" if _enabled else ""
    WHITE = "\033[37m" if _enabled else ""


# ─── Database ─────────────────────────────────────────────────────────────────

def get_db():
    """Get database connection, create tables if needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cost_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            period TEXT DEFAULT 'monthly',
            category TEXT DEFAULT 'other',
            description TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            month TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS token_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_date TEXT NOT NULL,
            model TEXT NOT NULL,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            estimated_cost_usd REAL DEFAULT 0.0,
            request_count INTEGER DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            cycle TEXT DEFAULT 'monthly',
            category TEXT DEFAULT 'subscription',
            renews_at TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monthly_limit REAL NOT NULL,
            currency TEXT DEFAULT 'EUR',
            alert_pct REAL DEFAULT 80.0,
            created_at TEXT NOT NULL
        );
        
        CREATE INDEX IF NOT EXISTS idx_entries_month ON cost_entries(month);
        CREATE INDEX IF NOT EXISTS idx_scans_date ON token_scans(scan_date);
    """)
    return conn


def get_config():
    """Load or create config."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {
        "default_currency": "EUR",
        "gateway_log_dir": os.path.expanduser("~/.openclaw/logs"),
        "created": datetime.now().isoformat()
    }


def save_config(config):
    """Save config."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


# ─── Token Scanning ──────────────────────────────────────────────────────────

def find_model_price(model_name):
    """Find pricing for a model, with fuzzy matching."""
    model_lower = model_name.lower()
    
    # Direct match
    for key, price in MODEL_PRICING.items():
        if key.lower() == model_lower:
            return price
    
    # Partial match (e.g., "claude-proxy/claude-opus-4-6" → "claude-opus-4-6")
    for key, price in MODEL_PRICING.items():
        if key.lower() in model_lower or model_lower.endswith(key.lower()):
            return price
    
    # Wildcard match (e.g., "ollama/*")
    for key, price in MODEL_PRICING.items():
        if key.endswith("/*"):
            prefix = key[:-2].lower()
            if model_lower.startswith(prefix):
                return price
    
    # Local/ollama models are free
    if any(x in model_lower for x in ["ollama", "local", "llama-local"]):
        return {"input": 0.0, "output": 0.0}
    
    return None


def scan_gateway_logs(days=1):
    """Scan OpenClaw gateway logs for token usage."""
    config = get_config()
    log_dir = Path(config.get("gateway_log_dir", os.path.expanduser("~/.openclaw/logs")))
    
    # Also check common log locations
    log_dirs = [
        log_dir,
        Path(os.path.expanduser("~/.openclaw/logs")),
        Path("/var/log/openclaw"),
        Path(os.path.expanduser("~/.openclaw/gateway/logs")),
    ]
    
    results = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "requests": 0})
    cutoff = datetime.now() - timedelta(days=days)
    files_scanned = 0
    lines_parsed = 0
    
    for ldir in log_dirs:
        if not ldir.exists():
            continue
            
        # Look for JSON log files and text log files
        for pattern in ["*.log", "*.jsonl", "*.json", "gateway*.log*"]:
            for log_file in sorted(ldir.glob(pattern)):
                try:
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mtime < cutoff - timedelta(days=1):
                        continue
                    
                    files_scanned += 1
                    with open(log_file, errors="ignore") as f:
                        for line in f:
                            lines_parsed += 1
                            try:
                                # Try JSON log format
                                if line.strip().startswith("{"):
                                    data = json.loads(line.strip())
                                    model = data.get("model", "")
                                    usage = data.get("usage", {})
                                    if model and usage:
                                        inp = usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0
                                        out = usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0
                                        results[model]["input_tokens"] += inp
                                        results[model]["output_tokens"] += out
                                        results[model]["requests"] += 1
                                        continue
                                
                                # Try text log patterns
                                # Pattern: "model=xxx tokens=NNN" or "tokens: {input: N, output: N}"
                                model_match = re.search(r'model[=:]\s*"?([a-zA-Z0-9_./-]+)"?', line)
                                token_match = re.search(r'(?:tokens|usage)[=:]\s*(\d+)', line)
                                if model_match and token_match:
                                    model = model_match.group(1)
                                    tokens = int(token_match.group(1))
                                    results[model]["output_tokens"] += tokens  # rough estimate
                                    results[model]["requests"] += 1
                                    
                            except (json.JSONDecodeError, ValueError, KeyError):
                                continue
                except (PermissionError, IOError):
                    continue
    
    return dict(results), files_scanned, lines_parsed


def cmd_scan_tokens(args):
    """Scan gateway logs and record token usage."""
    days = getattr(args, "days", 1)
    usage, files_scanned, lines_parsed = scan_gateway_logs(days)
    
    if not usage:
        print(f"{C.YELLOW}⚠ No token usage found in gateway logs.{C.RESET}")
        print(f"  Scanned {files_scanned} files, {lines_parsed} lines over last {days} day(s).")
        print(f"  Log directories checked: ~/.openclaw/logs, /var/log/openclaw")
        print(f"\n  {C.DIM}If your gateway logs are elsewhere, update config:{C.RESET}")
        print(f"  {C.DIM}Edit {CONFIG_PATH} → gateway_log_dir{C.RESET}")
        return
    
    db = get_db()
    scan_date = datetime.now().strftime("%Y-%m-%d")
    total_cost = 0.0
    rows = []
    
    for model, data in sorted(usage.items()):
        price = find_model_price(model)
        if price:
            cost = (data["input_tokens"] / 1_000_000 * price["input"] + 
                    data["output_tokens"] / 1_000_000 * price["output"])
        else:
            cost = 0.0  # unknown model
        
        total_tokens = data["input_tokens"] + data["output_tokens"]
        total_cost += cost
        
        db.execute("""
            INSERT INTO token_scans (scan_date, model, input_tokens, output_tokens, 
                                     total_tokens, estimated_cost_usd, request_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (scan_date, model, data["input_tokens"], data["output_tokens"],
              total_tokens, round(cost, 6), data["requests"]))
        
        rows.append({
            "model": model,
            "input_tokens": data["input_tokens"],
            "output_tokens": data["output_tokens"],
            "total_tokens": total_tokens,
            "requests": data["requests"],
            "cost_usd": round(cost, 6),
            "pricing_known": price is not None
        })
    
    db.commit()
    db.close()
    
    if getattr(args, "json", False):
        print(json.dumps({
            "scan_date": scan_date,
            "days_scanned": days,
            "files_scanned": files_scanned,
            "models": rows,
            "total_cost_usd": round(total_cost, 4)
        }, indent=2))
        return
    
    print(f"\n{C.BOLD}🔍 Token Scan — Last {days} day(s){C.RESET}")
    print(f"  {C.DIM}Scanned {files_scanned} files, {lines_parsed} lines{C.RESET}\n")
    
    if rows:
        # Header
        print(f"  {'Model':<35} {'In Tokens':>12} {'Out Tokens':>12} {'Requests':>8} {'Cost USD':>10}")
        print(f"  {'─'*35} {'─'*12} {'─'*12} {'─'*8} {'─'*10}")
        
        for r in sorted(rows, key=lambda x: x["cost_usd"], reverse=True):
            cost_str = f"${r['cost_usd']:.4f}" if r["pricing_known"] else f"${r['cost_usd']:.4f}?"
            color = C.RED if r["cost_usd"] > 1.0 else C.YELLOW if r["cost_usd"] > 0.1 else C.GREEN
            print(f"  {r['model']:<35} {r['input_tokens']:>12,} {r['output_tokens']:>12,} "
                  f"{r['requests']:>8,} {color}{cost_str:>10}{C.RESET}")
        
        print(f"\n  {C.BOLD}Total estimated: ${total_cost:.4f} USD{C.RESET}")
    else:
        print(f"  {C.DIM}No token data found{C.RESET}")


# ─── Cost Entry ───────────────────────────────────────────────────────────────

def cmd_track(args):
    """Record a cost entry."""
    now = datetime.now()
    month = now.strftime("%Y-%m")
    
    if args.category not in CATEGORIES:
        print(f"{C.RED}✗ Invalid category '{args.category}'. Use: {', '.join(CATEGORIES)}{C.RESET}")
        sys.exit(1)
    if args.period not in PERIODS:
        print(f"{C.RED}✗ Invalid period '{args.period}'. Use: {', '.join(PERIODS)}{C.RESET}")
        sys.exit(1)
    
    db = get_db()
    db.execute("""
        INSERT INTO cost_entries (provider, amount, currency, period, category, description, created_at, month)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (args.provider, args.amount, args.currency.upper(), args.period, 
          args.category, getattr(args, "description", "") or "", now.isoformat(), month))
    db.commit()
    db.close()
    
    if getattr(args, "json", False):
        print(json.dumps({"status": "ok", "provider": args.provider, 
                          "amount": args.amount, "currency": args.currency}))
    else:
        print(f"{C.GREEN}✓ Tracked: {args.provider} — {args.amount} {args.currency.upper()}/{args.period} [{args.category}]{C.RESET}")


# ─── Budget ───────────────────────────────────────────────────────────────────

def cmd_budget(args):
    """Set or show budget."""
    db = get_db()
    
    if args.monthly is not None:
        currency = getattr(args, "currency", "EUR") or "EUR"
        alert_pct = getattr(args, "alert_pct", 80.0) or 80.0
        
        # Replace existing budget
        db.execute("DELETE FROM budgets")
        db.execute("INSERT INTO budgets (monthly_limit, currency, alert_pct, created_at) VALUES (?, ?, ?, ?)",
                   (args.monthly, currency.upper(), alert_pct, datetime.now().isoformat()))
        db.commit()
        
        if getattr(args, "json", False):
            print(json.dumps({"status": "ok", "monthly": args.monthly, 
                              "currency": currency, "alert_pct": alert_pct}))
        else:
            print(f"{C.GREEN}✓ Budget set: {args.monthly} {currency.upper()}/month (alert at {alert_pct}%){C.RESET}")
    else:
        row = db.execute("SELECT * FROM budgets ORDER BY id DESC LIMIT 1").fetchone()
        if row:
            if getattr(args, "json", False):
                print(json.dumps(dict(row)))
            else:
                print(f"\n{C.BOLD}📊 Budget{C.RESET}")
                print(f"  Monthly limit: {row['monthly_limit']} {row['currency']}")
                print(f"  Alert threshold: {row['alert_pct']}%")
        else:
            print(f"{C.YELLOW}⚠ No budget set. Use: cost-guardian budget --monthly 50{C.RESET}")
    
    db.close()


# ─── Subscriptions ────────────────────────────────────────────────────────────

def cmd_sub(args):
    """Manage subscriptions."""
    db = get_db()
    action = args.sub_action
    
    if action == "add":
        try:
            db.execute("""
                INSERT INTO subscriptions (name, amount, currency, cycle, category, renews_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (args.name, args.amount, (args.currency or "USD").upper(), 
                  args.cycle or "monthly", args.category or "subscription",
                  args.renews or None, datetime.now().isoformat()))
            db.commit()
            print(f"{C.GREEN}✓ Subscription added: {args.name} — {args.amount} {(args.currency or 'USD').upper()}/{args.cycle or 'monthly'}{C.RESET}")
        except sqlite3.IntegrityError:
            print(f"{C.RED}✗ Subscription '{args.name}' already exists. Remove first.{C.RESET}")
    
    elif action == "remove":
        cursor = db.execute("DELETE FROM subscriptions WHERE name = ?", (args.name,))
        db.commit()
        if cursor.rowcount:
            print(f"{C.GREEN}✓ Removed subscription: {args.name}{C.RESET}")
        else:
            print(f"{C.YELLOW}⚠ No subscription found: {args.name}{C.RESET}")
    
    elif action == "list":
        rows = db.execute("SELECT * FROM subscriptions WHERE active = 1 ORDER BY amount DESC").fetchall()
        
        if getattr(args, "json", False):
            print(json.dumps([dict(r) for r in rows], indent=2))
            db.close()
            return
        
        if not rows:
            print(f"{C.DIM}No active subscriptions.{C.RESET}")
            db.close()
            return
        
        print(f"\n{C.BOLD}📋 Active Subscriptions{C.RESET}\n")
        total_monthly = 0
        print(f"  {'Name':<25} {'Amount':>10} {'Cycle':<10} {'Category':<15} {'Renews':<12}")
        print(f"  {'─'*25} {'─'*10} {'─'*10} {'─'*15} {'─'*12}")
        
        for r in rows:
            amt_str = f"{r['amount']:.2f} {r['currency']}"
            renews = r['renews_at'][:10] if r['renews_at'] else "—"
            print(f"  {r['name']:<25} {amt_str:>10} {r['cycle']:<10} {r['category']:<15} {renews:<12}")
            
            # Normalize to monthly
            multiplier = {"daily": 30, "weekly": 4.33, "monthly": 1, "yearly": 1/12}.get(r['cycle'], 1)
            total_monthly += r['amount'] * multiplier
        
        print(f"\n  {C.BOLD}Total monthly: ~{total_monthly:.2f} (mixed currencies){C.RESET}")
    
    elif action == "upcoming":
        days = getattr(args, "days", 14) or 14
        cutoff = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        
        rows = db.execute("""
            SELECT * FROM subscriptions 
            WHERE active = 1 AND renews_at IS NOT NULL AND renews_at <= ? AND renews_at >= ?
            ORDER BY renews_at ASC
        """, (cutoff, today)).fetchall()
        
        if getattr(args, "json", False):
            print(json.dumps([dict(r) for r in rows], indent=2))
            db.close()
            return
        
        if not rows:
            print(f"{C.GREEN}✓ No renewals in the next {days} days.{C.RESET}")
        else:
            print(f"\n{C.BOLD}🔔 Upcoming Renewals (next {days} days){C.RESET}\n")
            for r in rows:
                days_until = (datetime.strptime(r['renews_at'][:10], "%Y-%m-%d") - datetime.now()).days
                urgency = C.RED if days_until <= 3 else C.YELLOW if days_until <= 7 else C.GREEN
                print(f"  {urgency}● {r['name']}: {r['amount']} {r['currency']} — renews in {days_until}d ({r['renews_at'][:10]}){C.RESET}")
    
    db.close()


# ─── Report ───────────────────────────────────────────────────────────────────

def get_monthly_costs(db, month):
    """Get all costs for a given month."""
    entries = db.execute("SELECT * FROM cost_entries WHERE month = ?", (month,)).fetchall()
    token_scans = db.execute("""
        SELECT model, SUM(input_tokens) as inp, SUM(output_tokens) as out, 
               SUM(estimated_cost_usd) as cost, SUM(request_count) as reqs
        FROM token_scans WHERE scan_date LIKE ?
        GROUP BY model
    """, (f"{month}%",)).fetchall()
    subs = db.execute("SELECT * FROM subscriptions WHERE active = 1").fetchall()
    
    return entries, token_scans, subs


def cmd_report(args):
    """Generate cost report."""
    period = getattr(args, "period", "month") or "month"
    month = getattr(args, "month", None) or datetime.now().strftime("%Y-%m")
    
    db = get_db()
    entries, token_scans, subs = get_monthly_costs(db, month)
    budget_row = db.execute("SELECT * FROM budgets ORDER BY id DESC LIMIT 1").fetchone()
    
    # Calculate totals
    by_category = defaultdict(float)
    by_provider = defaultdict(float)
    total_manual = 0.0
    
    for e in entries:
        by_category[e["category"]] += e["amount"]
        by_provider[e["provider"]] += e["amount"]
        total_manual += e["amount"]
    
    # Token-based costs
    total_tokens_cost = 0.0
    token_details = []
    for ts in token_scans:
        total_tokens_cost += ts["cost"]
        token_details.append({
            "model": ts["model"],
            "input_tokens": ts["inp"],
            "output_tokens": ts["out"],
            "cost_usd": round(ts["cost"], 4),
            "requests": ts["reqs"]
        })
    
    # Subscription costs (monthly equivalent)
    total_subs = 0.0
    sub_details = []
    for s in subs:
        multiplier = {"daily": 30, "weekly": 4.33, "monthly": 1, "yearly": 1/12}.get(s["cycle"], 1)
        monthly_cost = s["amount"] * multiplier
        total_subs += monthly_cost
        sub_details.append({"name": s["name"], "monthly_cost": round(monthly_cost, 2), 
                           "currency": s["currency"]})
    
    grand_total = total_manual + total_tokens_cost + total_subs
    
    if getattr(args, "json", False):
        report = {
            "month": month,
            "manual_entries": total_manual,
            "token_costs_usd": round(total_tokens_cost, 4),
            "subscription_costs": round(total_subs, 2),
            "grand_total": round(grand_total, 2),
            "by_category": dict(by_category),
            "by_provider": dict(by_provider),
            "token_breakdown": token_details,
            "subscription_breakdown": sub_details,
            "budget": dict(budget_row) if budget_row else None
        }
        print(json.dumps(report, indent=2))
        db.close()
        return
    
    # Human-readable report
    print(f"\n{C.BOLD}💰 Cost Report — {month}{C.RESET}")
    print(f"{'═'*60}")
    
    # Manual entries by category
    if by_category:
        print(f"\n{C.CYAN}📋 Tracked Costs{C.RESET}")
        for cat, amt in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            bar_len = int(min(amt / max(by_category.values(), default=1) * 20, 20))
            bar = "█" * bar_len
            print(f"  {cat:<15} {amt:>8.2f}  {C.BLUE}{bar}{C.RESET}")
    
    # Token costs
    if token_details:
        print(f"\n{C.CYAN}🤖 AI Token Costs (estimated){C.RESET}")
        for td in sorted(token_details, key=lambda x: x["cost_usd"], reverse=True):
            if td["cost_usd"] > 0:
                print(f"  {td['model']:<35} ${td['cost_usd']:>8.4f}  ({td['requests']} req, "
                      f"{td['input_tokens']:,}in/{td['output_tokens']:,}out)")
    
    # Subscriptions
    if sub_details:
        print(f"\n{C.CYAN}🔄 Subscriptions (monthly equiv.){C.RESET}")
        for sd in sorted(sub_details, key=lambda x: x["monthly_cost"], reverse=True):
            print(f"  {sd['name']:<25} {sd['monthly_cost']:>8.2f} {sd['currency']}")
    
    # Grand total
    print(f"\n{'─'*60}")
    print(f"  {C.BOLD}Manual tracked:     {total_manual:>10.2f}{C.RESET}")
    print(f"  {C.BOLD}Token costs (USD):  ${total_tokens_cost:>9.4f}{C.RESET}")
    print(f"  {C.BOLD}Subscriptions:      {total_subs:>10.2f}{C.RESET}")
    print(f"  {C.BOLD}{'─'*30}{C.RESET}")
    
    color = C.RED if grand_total > 100 else C.YELLOW if grand_total > 50 else C.GREEN
    print(f"  {color}{C.BOLD}GRAND TOTAL:        {grand_total:>10.2f}{C.RESET}")
    
    # Budget check
    if budget_row:
        limit = budget_row["monthly_limit"]
        pct = (grand_total / limit * 100) if limit > 0 else 0
        bar_len = int(min(pct / 100 * 30, 30))
        bar_color = C.RED if pct > 100 else C.YELLOW if pct > budget_row["alert_pct"] else C.GREEN
        bar = "█" * bar_len + "░" * (30 - bar_len)
        
        print(f"\n{C.BOLD}📊 Budget: {limit} {budget_row['currency']}/month{C.RESET}")
        print(f"  {bar_color}[{bar}] {pct:.1f}%{C.RESET}")
        
        if pct > 100:
            print(f"  {C.RED}⚠ OVER BUDGET by {grand_total - limit:.2f}!{C.RESET}")
        elif pct > budget_row["alert_pct"]:
            print(f"  {C.YELLOW}⚠ Approaching budget limit ({pct:.1f}% of {limit}){C.RESET}")
        else:
            remaining = limit - grand_total
            print(f"  {C.GREEN}✓ {remaining:.2f} remaining{C.RESET}")
    
    db.close()


# ─── Optimize ─────────────────────────────────────────────────────────────────

def cmd_optimize(args):
    """Generate optimization recommendations."""
    db = get_db()
    
    # Get last 30 days of token scans
    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    token_data = db.execute("""
        SELECT model, SUM(input_tokens) as inp, SUM(output_tokens) as out,
               SUM(estimated_cost_usd) as cost, SUM(request_count) as reqs
        FROM token_scans WHERE scan_date >= ?
        GROUP BY model ORDER BY cost DESC
    """, (cutoff,)).fetchall()
    
    subs = db.execute("SELECT * FROM subscriptions WHERE active = 1").fetchall()
    entries = db.execute("SELECT * FROM cost_entries ORDER BY created_at DESC LIMIT 100").fetchall()
    
    recommendations = []
    
    # 1. Model optimization
    for td in token_data:
        model = td["model"]
        cost = td["cost"]
        reqs = td["reqs"]
        
        if cost <= 0:
            continue
        
        # Suggest cheaper alternatives
        if "opus" in model.lower() or "gpt-4o" == model.lower():
            cheaper = "claude-3-5-haiku" if "claude" in model.lower() else "gpt-4o-mini"
            savings_pct = 85 if "opus" in model.lower() else 90
            est_savings = cost * savings_pct / 100
            recommendations.append({
                "type": "model_switch",
                "priority": "high" if est_savings > 5 else "medium",
                "current": model,
                "suggested": cheaper,
                "estimated_savings_usd": round(est_savings, 2),
                "detail": f"Switch {model} → {cheaper} for routine tasks. Est. savings: ${est_savings:.2f}/month ({savings_pct}% cheaper). Keep {model} for complex reasoning only."
            })
        
        # High request count with expensive model
        if reqs > 100 and cost > 2:
            recommendations.append({
                "type": "request_reduction",
                "priority": "medium",
                "model": model,
                "requests": reqs,
                "detail": f"{model}: {reqs} requests in 30 days costing ${cost:.2f}. Consider batching requests or reducing cron frequency."
            })
    
    # 2. Subscription optimization
    for s in subs:
        # Flag expensive subscriptions
        if s["amount"] > 20:
            recommendations.append({
                "type": "subscription_review",
                "priority": "low",
                "name": s["name"],
                "amount": s["amount"],
                "detail": f"Review '{s['name']}' ({s['amount']} {s['currency']}/{s['cycle']}). Is this actively used? Consider downgrading or cancelling."
            })
    
    # 3. General recommendations
    if not token_data:
        recommendations.append({
            "type": "setup",
            "priority": "high",
            "detail": "No token scan data found. Run 'cost-guardian scan-tokens' regularly to track AI costs."
        })
    
    # Check for local model usage opportunity
    has_expensive = any(td["cost"] > 1 for td in token_data)
    has_local = any("ollama" in td["model"].lower() or td["cost"] == 0 for td in token_data)
    if has_expensive and not has_local:
        recommendations.append({
            "type": "local_models",
            "priority": "medium",
            "detail": "No local model usage detected. Consider Ollama for simple tasks (classification, extraction, formatting) — $0 cost."
        })
    
    db.close()
    
    if getattr(args, "json", False):
        print(json.dumps({"recommendations": recommendations, 
                          "count": len(recommendations)}, indent=2))
        return
    
    print(f"\n{C.BOLD}🎯 Optimization Recommendations{C.RESET}")
    print(f"{'═'*60}\n")
    
    if not recommendations:
        print(f"  {C.GREEN}✓ No obvious optimizations found. Costs look efficient!{C.RESET}")
        return
    
    priority_colors = {"high": C.RED, "medium": C.YELLOW, "low": C.BLUE}
    priority_icons = {"high": "🔴", "medium": "🟡", "low": "🔵"}
    
    for i, rec in enumerate(recommendations, 1):
        p = rec["priority"]
        color = priority_colors.get(p, C.WHITE)
        icon = priority_icons.get(p, "●")
        print(f"  {icon} [{p.upper()}] {rec['type']}")
        print(f"     {color}{rec['detail']}{C.RESET}")
        if "estimated_savings_usd" in rec:
            print(f"     {C.GREEN}💰 Potential savings: ${rec['estimated_savings_usd']}/month{C.RESET}")
        print()


# ─── Forecast ─────────────────────────────────────────────────────────────────

def cmd_forecast(args):
    """Forecast future spending."""
    months_ahead = getattr(args, "months", 3) or 3
    db = get_db()
    
    # Get last 3 months of data for trend
    now = datetime.now()
    monthly_totals = []
    
    for i in range(3, 0, -1):
        m = (now - timedelta(days=30*i)).strftime("%Y-%m")
        entries = db.execute("SELECT SUM(amount) as total FROM cost_entries WHERE month = ?", (m,)).fetchone()
        tokens = db.execute("""
            SELECT SUM(estimated_cost_usd) as total FROM token_scans WHERE scan_date LIKE ?
        """, (f"{m}%",)).fetchone()
        
        e_total = entries["total"] or 0
        t_total = tokens["total"] or 0
        monthly_totals.append({"month": m, "total": e_total + t_total})
    
    # Current month
    current_month = now.strftime("%Y-%m")
    current_entries = db.execute("SELECT SUM(amount) as total FROM cost_entries WHERE month = ?", 
                                 (current_month,)).fetchone()
    current_tokens = db.execute("""
        SELECT SUM(estimated_cost_usd) as total FROM token_scans WHERE scan_date LIKE ?
    """, (f"{current_month}%",)).fetchone()
    
    # Subscriptions monthly
    subs = db.execute("SELECT * FROM subscriptions WHERE active = 1").fetchall()
    sub_monthly = sum(
        s["amount"] * {"daily": 30, "weekly": 4.33, "monthly": 1, "yearly": 1/12}.get(s["cycle"], 1)
        for s in subs
    )
    
    current_total = (current_entries["total"] or 0) + (current_tokens["total"] or 0) + sub_monthly
    monthly_totals.append({"month": current_month, "total": current_total})
    
    # Calculate trend (simple linear)
    non_zero = [m for m in monthly_totals if m["total"] > 0]
    if len(non_zero) >= 2:
        avg_growth = (non_zero[-1]["total"] - non_zero[0]["total"]) / len(non_zero)
        base = non_zero[-1]["total"]
    elif non_zero:
        avg_growth = 0
        base = non_zero[-1]["total"]
    else:
        avg_growth = 0
        base = sub_monthly  # only subscriptions
    
    # Generate forecast
    forecasts = []
    budget_row = db.execute("SELECT * FROM budgets ORDER BY id DESC LIMIT 1").fetchone()
    budget_limit = budget_row["monthly_limit"] if budget_row else None
    
    for i in range(1, months_ahead + 1):
        forecast_month = (now + timedelta(days=30*i)).strftime("%Y-%m")
        predicted = max(0, base + avg_growth * i)
        over_budget = predicted > budget_limit if budget_limit else None
        forecasts.append({
            "month": forecast_month,
            "predicted": round(predicted, 2),
            "over_budget": over_budget
        })
    
    db.close()
    
    if getattr(args, "json", False):
        print(json.dumps({
            "historical": monthly_totals,
            "forecast": forecasts,
            "trend_monthly": round(avg_growth, 2),
            "subscription_baseline": round(sub_monthly, 2),
            "budget_limit": budget_limit
        }, indent=2))
        return
    
    print(f"\n{C.BOLD}📈 Spend Forecast — Next {months_ahead} Month(s){C.RESET}")
    print(f"{'═'*60}\n")
    
    # Historical
    print(f"  {C.DIM}Historical:{C.RESET}")
    for m in monthly_totals:
        bar_len = int(min(m["total"] / max(m["total"] for m in monthly_totals if m["total"] > 0) * 25, 25)) if any(mt["total"] > 0 for mt in monthly_totals) else 0
        bar = "█" * max(bar_len, 1)
        print(f"  {m['month']}  {m['total']:>8.2f}  {C.BLUE}{bar}{C.RESET}")
    
    # Trend
    trend_icon = "📈" if avg_growth > 0 else "📉" if avg_growth < 0 else "➡️"
    print(f"\n  {C.DIM}Trend: {trend_icon} {avg_growth:+.2f}/month | Subscriptions baseline: {sub_monthly:.2f}/month{C.RESET}\n")
    
    # Forecast
    print(f"  {C.BOLD}Forecast:{C.RESET}")
    for f in forecasts:
        color = C.RED if f["over_budget"] else C.GREEN
        budget_note = f" {C.RED}⚠ OVER BUDGET{C.RESET}" if f["over_budget"] else ""
        bar_max = max(ff["predicted"] for ff in forecasts) if forecasts else 1
        bar_len = int(min(f["predicted"] / bar_max * 25, 25)) if bar_max > 0 else 0
        bar = "▓" * max(bar_len, 1)
        print(f"  {f['month']}  {color}{f['predicted']:>8.2f}{C.RESET}  {C.MAGENTA}{bar}{C.RESET}{budget_note}")
    
    if budget_limit:
        print(f"\n  Budget limit: {budget_limit}/month")


# ─── Status ───────────────────────────────────────────────────────────────────

def cmd_status(args):
    """Quick status dashboard."""
    db = get_db()
    now = datetime.now()
    month = now.strftime("%Y-%m")
    
    # Current month costs
    entries_total = db.execute("SELECT SUM(amount) as t FROM cost_entries WHERE month = ?", (month,)).fetchone()["t"] or 0
    token_total = db.execute("SELECT SUM(estimated_cost_usd) as t FROM token_scans WHERE scan_date LIKE ?", 
                              (f"{month}%",)).fetchone()["t"] or 0
    
    # Subscriptions
    subs = db.execute("SELECT * FROM subscriptions WHERE active = 1").fetchall()
    sub_monthly = sum(
        s["amount"] * {"daily": 30, "weekly": 4.33, "monthly": 1, "yearly": 1/12}.get(s["cycle"], 1)
        for s in subs
    )
    
    # Budget
    budget = db.execute("SELECT * FROM budgets ORDER BY id DESC LIMIT 1").fetchone()
    
    # Last scan
    last_scan = db.execute("SELECT scan_date FROM token_scans ORDER BY id DESC LIMIT 1").fetchone()
    
    # Entry counts
    entry_count = db.execute("SELECT COUNT(*) as c FROM cost_entries WHERE month = ?", (month,)).fetchone()["c"]
    scan_count = db.execute("SELECT COUNT(DISTINCT scan_date) as c FROM token_scans WHERE scan_date LIKE ?", 
                             (f"{month}%",)).fetchone()["c"]
    sub_count = len(subs)
    
    grand_total = entries_total + token_total + sub_monthly
    
    if getattr(args, "json", False):
        print(json.dumps({
            "month": month,
            "manual_costs": round(entries_total, 2),
            "token_costs_usd": round(token_total, 4),
            "subscription_costs": round(sub_monthly, 2),
            "grand_total": round(grand_total, 2),
            "entry_count": entry_count,
            "scan_days": scan_count,
            "subscription_count": sub_count,
            "last_scan": last_scan["scan_date"] if last_scan else None,
            "budget": dict(budget) if budget else None
        }, indent=2))
        db.close()
        return
    
    print(f"\n{C.BOLD}💰 Cost Guardian — Status{C.RESET}")
    print(f"{'═'*45}")
    print(f"  Month:          {C.CYAN}{month}{C.RESET}")
    print(f"  Manual costs:   {entries_total:>10.2f}  ({entry_count} entries)")
    print(f"  Token costs:    ${token_total:>9.4f}  ({scan_count} scan days)")
    print(f"  Subscriptions:  {sub_monthly:>10.2f}  ({sub_count} active)")
    print(f"  {'─'*35}")
    
    color = C.RED if grand_total > 100 else C.YELLOW if grand_total > 50 else C.GREEN
    print(f"  {color}{C.BOLD}Total:            {grand_total:>10.2f}{C.RESET}")
    
    if budget:
        pct = (grand_total / budget["monthly_limit"] * 100) if budget["monthly_limit"] > 0 else 0
        bar_len = int(min(pct / 100 * 20, 20))
        bar_color = C.RED if pct > 100 else C.YELLOW if pct > budget["alert_pct"] else C.GREEN
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"\n  Budget: [{bar_color}{bar}{C.RESET}] {pct:.0f}% of {budget['monthly_limit']} {budget['currency']}")
    
    if last_scan:
        print(f"\n  {C.DIM}Last token scan: {last_scan['scan_date']}{C.RESET}")
    else:
        print(f"\n  {C.YELLOW}⚠ No token scans yet. Run: cost-guardian scan-tokens{C.RESET}")
    
    db.close()


# ─── Init ─────────────────────────────────────────────────────────────────────

def cmd_init(args):
    """Initialize cost-guardian."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    config = get_config()
    if not CONFIG_PATH.exists():
        save_config(config)
    
    # Create database
    db = get_db()
    db.close()
    
    if getattr(args, "json", False):
        print(json.dumps({"status": "ok", "data_dir": str(DATA_DIR), 
                          "db": str(DB_PATH), "config": str(CONFIG_PATH)}))
    else:
        print(f"{C.GREEN}✓ cost-guardian initialized{C.RESET}")
        print(f"  Data dir: {DATA_DIR}")
        print(f"  Database: {DB_PATH}")
        print(f"  Config:   {CONFIG_PATH}")
        print(f"\n  Next steps:")
        print(f"  1. Set budget:     cost-guardian budget --monthly 50")
        print(f"  2. Track costs:    cost-guardian track --provider X --amount N --category api")
        print(f"  3. Scan tokens:    cost-guardian scan-tokens")
        print(f"  4. View report:    cost-guardian report")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="cost-guardian",
        description="AI & Infrastructure Cost Tracker — track, analyze, optimize spending",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cost-guardian init                                    Initialize
  cost-guardian track --provider openai --amount 12.50 --category api
  cost-guardian scan-tokens --days 7                    Scan gateway logs
  cost-guardian budget --monthly 50                     Set budget
  cost-guardian report                                  Monthly report
  cost-guardian optimize                                Get recommendations
  cost-guardian forecast --months 6                     Forecast spending
  cost-guardian sub add --name OpenRouter --amount 20   Add subscription
  cost-guardian status                                  Quick dashboard
        """
    )
    parser.add_argument("--version", action="version", version=f"cost-guardian {VERSION}")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # init
    p_init = subparsers.add_parser("init", help="Initialize cost-guardian")
    p_init.add_argument("--json", action="store_true")
    
    # track
    p_track = subparsers.add_parser("track", help="Record a cost entry")
    p_track.add_argument("--provider", required=True, help="Provider name (openai, hetzner, etc.)")
    p_track.add_argument("--amount", type=float, required=True, help="Cost amount")
    p_track.add_argument("--currency", default="USD", help="Currency (default: USD)")
    p_track.add_argument("--period", default="monthly", choices=PERIODS, help="Billing period")
    p_track.add_argument("--category", default="other", choices=CATEGORIES, help="Cost category")
    p_track.add_argument("--description", "-d", default="", help="Description")
    p_track.add_argument("--json", action="store_true")
    
    # scan-tokens
    p_scan = subparsers.add_parser("scan-tokens", help="Scan gateway logs for token usage")
    p_scan.add_argument("--days", type=int, default=1, help="Days to scan (default: 1)")
    p_scan.add_argument("--json", action="store_true")
    
    # budget
    p_budget = subparsers.add_parser("budget", help="Set or view budget")
    p_budget.add_argument("--monthly", type=float, help="Monthly budget limit")
    p_budget.add_argument("--currency", default="EUR", help="Budget currency")
    p_budget.add_argument("--alert-pct", type=float, default=80, help="Alert threshold percentage")
    p_budget.add_argument("--json", action="store_true")
    
    # report
    p_report = subparsers.add_parser("report", help="Generate cost report")
    p_report.add_argument("--period", choices=["week", "month"], default="month")
    p_report.add_argument("--month", help="Specific month (YYYY-MM)")
    p_report.add_argument("--json", action="store_true")
    
    # optimize
    p_opt = subparsers.add_parser("optimize", help="Get optimization recommendations")
    p_opt.add_argument("--json", action="store_true")
    
    # forecast
    p_forecast = subparsers.add_parser("forecast", help="Forecast future spending")
    p_forecast.add_argument("--months", type=int, default=3, help="Months to forecast")
    p_forecast.add_argument("--json", action="store_true")
    
    # sub (subscriptions)
    p_sub = subparsers.add_parser("sub", help="Manage subscriptions")
    sub_subs = p_sub.add_subparsers(dest="sub_action", help="Subscription action")
    
    p_sub_add = sub_subs.add_parser("add", help="Add subscription")
    p_sub_add.add_argument("--name", required=True, help="Subscription name")
    p_sub_add.add_argument("--amount", type=float, required=True, help="Amount")
    p_sub_add.add_argument("--currency", default="USD")
    p_sub_add.add_argument("--cycle", default="monthly", choices=["daily", "weekly", "monthly", "yearly"])
    p_sub_add.add_argument("--category", default="subscription", choices=CATEGORIES)
    p_sub_add.add_argument("--renews", help="Next renewal date (YYYY-MM-DD)")
    
    p_sub_rm = sub_subs.add_parser("remove", help="Remove subscription")
    p_sub_rm.add_argument("--name", required=True)
    
    p_sub_list = sub_subs.add_parser("list", help="List subscriptions")
    p_sub_list.add_argument("--json", action="store_true")
    
    p_sub_up = sub_subs.add_parser("upcoming", help="Upcoming renewals")
    p_sub_up.add_argument("--days", type=int, default=14, help="Days ahead to check")
    p_sub_up.add_argument("--json", action="store_true")
    
    # status
    p_status = subparsers.add_parser("status", help="Quick status dashboard")
    p_status.add_argument("--json", action="store_true")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    commands = {
        "init": cmd_init,
        "track": cmd_track,
        "scan-tokens": cmd_scan_tokens,
        "budget": cmd_budget,
        "report": cmd_report,
        "optimize": cmd_optimize,
        "forecast": cmd_forecast,
        "sub": cmd_sub,
        "status": cmd_status,
    }
    
    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
