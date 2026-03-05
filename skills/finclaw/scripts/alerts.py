#!/usr/bin/env python3
"""Price alerts: create, delete, list, snooze."""

import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.db import get_connection
from lib.formatters import detect_asset_type


def create_alert(symbol, condition, target_value, current_price=None, note=None):
    symbol = symbol.upper()
    asset_type = detect_asset_type(symbol)
    conn = get_connection()
    try:
        aid = conn.execute("INSERT INTO alerts (symbol, asset_type, condition, target_value, current_value_at_creation, note) VALUES (?,?,?,?,?,?)",
                           (symbol, asset_type, condition, target_value, current_price, note)).lastrowid
        conn.commit()
        cond = {"above": f"goes above {target_value}", "below": f"drops below {target_value}",
                "change_pct": f"changes by {target_value}%", "volume_above": f"volume exceeds {target_value}"}
        return f"Alert #{aid} created: {symbol} {cond.get(condition, condition)}\nStatus: active"
    finally: conn.close()


def delete_alert(aid):
    conn = get_connection()
    try:
        row = conn.execute("SELECT symbol FROM alerts WHERE id=?", (aid,)).fetchone()
        if not row: return f"Error: Alert #{aid} not found"
        conn.execute("UPDATE alerts SET status='deleted' WHERE id=?", (aid,))
        conn.commit()
        return f"Alert #{aid} ({row['symbol']}) deleted."
    finally: conn.close()


def snooze_alert(aid, hours=24):
    conn = get_connection()
    try:
        conn.execute("UPDATE alerts SET status='snoozed', snoozed_until=datetime('now', ? || ' hours') WHERE id=?", (str(hours), aid))
        conn.commit()
        return f"Alert #{aid} snoozed for {hours} hours."
    finally: conn.close()


def list_alerts(status=None):
    conn = get_connection()
    try:
        if status:
            alerts = conn.execute("SELECT * FROM alerts WHERE status=? ORDER BY created_at DESC", (status,)).fetchall()
        else:
            alerts = conn.execute("SELECT * FROM alerts WHERE status != 'deleted' ORDER BY status, created_at DESC").fetchall()
        if not alerts: return "No alerts found."
        lines = ["**Price Alerts**\n"]
        for a in alerts:
            icon = {"active": "🟢", "triggered": "🔔", "snoozed": "💤"}.get(a["status"], "⚪")
            cond = {"above": f"> {a['target_value']}", "below": f"< {a['target_value']}",
                    "change_pct": f"±{a['target_value']}%", "volume_above": f"vol > {a['target_value']}"}.get(a["condition"], a["condition"])
            line = f"  {icon} #{a['id']} {a['symbol']} {cond} [{a['status']}]"
            if a["note"]: line += f" — {a['note']}"
            lines.append(line)
        return "\n".join(lines)
    finally: conn.close()


def main():
    parser = argparse.ArgumentParser(description="Price alerts")
    parser.add_argument("action", choices=["create", "delete", "list", "snooze"])
    parser.add_argument("--symbol", "-s"); parser.add_argument("--condition", "-c", choices=["above", "below", "change_pct", "volume_above"])
    parser.add_argument("--target", "-t", type=float); parser.add_argument("--current-price", type=float)
    parser.add_argument("--note"); parser.add_argument("--id", type=int)
    parser.add_argument("--status"); parser.add_argument("--hours", type=int, default=24)
    args = parser.parse_args()

    if args.action == "create":
        if not all([args.symbol, args.condition, args.target]): print("Error: --symbol, --condition, --target required"); sys.exit(1)
        print(create_alert(args.symbol, args.condition, args.target, args.current_price, args.note))
    elif args.action == "delete":
        if not args.id: print("Error: --id required"); sys.exit(1)
        print(delete_alert(args.id))
    elif args.action == "snooze":
        if not args.id: print("Error: --id required"); sys.exit(1)
        print(snooze_alert(args.id, args.hours))
    elif args.action == "list": print(list_alerts(args.status))


if __name__ == "__main__":
    main()
