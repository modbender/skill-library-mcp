#!/usr/bin/env python3
"""Budget Tracker for OpenClaw agents.

Track spending, enforce limits, prevent surprise bills.
Data stored in ~/.openclaw/budget-tracker/budget.json by default.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DATA_DIR = os.path.expanduser("~/.openclaw/budget-tracker")


def get_data_path(data_dir=None):
    d = Path(data_dir or DEFAULT_DATA_DIR)
    d.mkdir(parents=True, exist_ok=True)
    return d / "budget.json"


def load_data(data_dir=None):
    path = get_data_path(data_dir)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {
        "budget": {"total": 0.0, "alert_threshold": 0.0},
        "transactions": []
    }


def save_data(data, data_dir=None):
    path = get_data_path(data_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def total_spent(data):
    return sum(t["amount"] for t in data["transactions"])


def remaining(data):
    return data["budget"]["total"] - total_spent(data)


def cmd_log(args, data):
    txn_id = f"txn_{len(data['transactions']) + 1:04d}"
    txn = {
        "id": txn_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "amount": args.amount,
        "merchant": args.merchant or "unknown",
        "category": args.category or "other",
        "note": args.note or ""
    }
    data["transactions"].append(txn)
    save_data(data, args.data_dir)

    bal = remaining(data)
    print(f"Logged: ${args.amount:.2f} to {txn['merchant']} ({txn['category']})")
    print(f"Remaining budget: ${bal:.2f}")

    if data["budget"]["alert_threshold"] > 0 and bal < data["budget"]["alert_threshold"]:
        print(f"⚠️  WARNING: Balance ${bal:.2f} is below alert threshold ${data['budget']['alert_threshold']:.2f}")

    if bal < 0:
        print(f"🚨 OVER BUDGET by ${abs(bal):.2f}!")


def cmd_balance(args, data):
    spent = total_spent(data)
    bal = remaining(data)
    budget = data["budget"]["total"]
    pct = (spent / budget * 100) if budget > 0 else 0

    print(f"Budget:    ${budget:.2f}")
    print(f"Spent:     ${spent:.2f} ({pct:.1f}%)")
    print(f"Remaining: ${bal:.2f}")

    if data["budget"]["alert_threshold"] > 0 and bal < data["budget"]["alert_threshold"]:
        print(f"⚠️  Below alert threshold (${data['budget']['alert_threshold']:.2f})")


def cmd_summary(args, data):
    by_category = {}
    by_merchant = {}
    for t in data["transactions"]:
        cat = t.get("category", "other")
        mer = t.get("merchant", "unknown")
        by_category[cat] = by_category.get(cat, 0) + t["amount"]
        by_merchant[mer] = by_merchant.get(mer, 0) + t["amount"]

    spent = total_spent(data)
    bal = remaining(data)
    count = len(data["transactions"])

    print(f"=== Budget Summary ===")
    print(f"Total budget: ${data['budget']['total']:.2f}")
    print(f"Total spent:  ${spent:.2f}")
    print(f"Remaining:    ${bal:.2f}")
    print(f"Transactions: {count}")
    print()

    if by_category:
        print("By Category:")
        for cat, amt in sorted(by_category.items(), key=lambda x: -x[1]):
            print(f"  {cat}: ${amt:.2f}")
        print()

    if by_merchant:
        print("By Merchant:")
        for mer, amt in sorted(by_merchant.items(), key=lambda x: -x[1]):
            print(f"  {mer}: ${amt:.2f}")


def cmd_history(args, data):
    limit = args.limit or 10
    txns = data["transactions"][-limit:]
    if not txns:
        print("No transactions yet.")
        return

    print(f"Last {len(txns)} transactions:")
    for t in txns:
        ts = t["timestamp"][:19].replace("T", " ")
        print(f"  [{ts}] ${t['amount']:.2f} — {t['merchant']} ({t['category']}){' — ' + t['note'] if t.get('note') else ''}")


def cmd_set_budget(args, data):
    data["budget"]["total"] = args.total
    save_data(data, args.data_dir)
    print(f"Budget set to ${args.total:.2f}")
    print(f"Current spent: ${total_spent(data):.2f}")
    print(f"Remaining: ${remaining(data):.2f}")


def cmd_set_alert(args, data):
    data["budget"]["alert_threshold"] = args.threshold
    save_data(data, args.data_dir)
    print(f"Alert threshold set to ${args.threshold:.2f}")


def cmd_check(args, data):
    bal = remaining(data)
    if args.amount <= bal:
        print(f"✅ Safe to spend ${args.amount:.2f} (${bal:.2f} remaining, ${bal - args.amount:.2f} after)")
    elif args.amount <= bal + data["budget"]["alert_threshold"]:
        print(f"⚠️  Possible — ${args.amount:.2f} would leave only ${bal - args.amount:.2f} (below alert threshold)")
    else:
        print(f"🚨 BLOCKED — ${args.amount:.2f} exceeds remaining budget of ${bal:.2f}")
        sys.exit(1)


def cmd_export(args, data):
    fmt = args.format or "csv"
    if fmt == "csv":
        print("id,timestamp,amount,merchant,category,note")
        for t in data["transactions"]:
            note = t.get("note", "").replace(",", ";")
            print(f"{t['id']},{t['timestamp']},{t['amount']},{t['merchant']},{t['category']},{note}")
    elif fmt == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Unknown format: {fmt}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Budget Tracker for OpenClaw agents")
    parser.add_argument("--data-dir", help="Override data directory")
    sub = parser.add_subparsers(dest="command")

    p_log = sub.add_parser("log", help="Log a transaction")
    p_log.add_argument("--amount", type=float, required=True)
    p_log.add_argument("--merchant", default="unknown")
    p_log.add_argument("--category", default="other")
    p_log.add_argument("--note", default="")

    sub.add_parser("balance", help="Check current balance")
    sub.add_parser("summary", help="Spending summary")

    p_hist = sub.add_parser("history", help="Recent transactions")
    p_hist.add_argument("--limit", type=int, default=10)

    p_budget = sub.add_parser("set-budget", help="Set total budget")
    p_budget.add_argument("--total", type=float, required=True)

    p_alert = sub.add_parser("set-alert", help="Set alert threshold")
    p_alert.add_argument("--threshold", type=float, required=True)

    p_check = sub.add_parser("check", help="Check if purchase is safe")
    p_check.add_argument("--amount", type=float, required=True)

    p_export = sub.add_parser("export", help="Export data")
    p_export.add_argument("--format", choices=["csv", "json"], default="csv")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    data = load_data(args.data_dir)

    cmds = {
        "log": cmd_log,
        "balance": cmd_balance,
        "summary": cmd_summary,
        "history": cmd_history,
        "set-budget": cmd_set_budget,
        "set-alert": cmd_set_alert,
        "check": cmd_check,
        "export": cmd_export,
    }

    cmds[args.command](args, data)


if __name__ == "__main__":
    main()
