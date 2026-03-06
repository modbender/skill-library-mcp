#!/usr/bin/env python3
"""
Claude Max subscription usage calculator for OpenClaw.
Scans session JSONL files and calculates credits consumed since the weekly reset.

Features:
  - Weekly overview with progress bar
  - 5-hour sliding window rate limit warning
  - Per-session breakdown (all or top N)
  - Single session deep-dive (--session)
  - Saved config for reset time/plan (--save)
  - JSON output for programmatic use

Based on: https://she-llac.com/claude-limits
"""

import json, glob, os, sys, argparse, math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# --- Credits rates (reverse-engineered) ---
# credits = (input_tokens + cache_write_tokens) * input_rate + output_tokens * output_rate
# Cache reads are FREE on subscription plans.
CREDIT_RATES = {
    "haiku":  {"input": 2/15, "output": 10/15},
    "sonnet": {"input": 6/15, "output": 30/15},
    "opus":   {"input": 10/15, "output": 50/15},
}

PLANS = {
    "pro":  {"price": 20,  "per_5h": 550_000,     "per_week": 5_000_000},
    "5x":   {"price": 100, "per_5h": 3_300_000,    "per_week": 41_666_700},
    "20x":  {"price": 200, "per_5h": 11_000_000,   "per_week": 83_333_300},
}

CONFIG_PATH = os.path.expanduser("~/.openclaw/claude-usage.json")


def get_tier(model_name: str) -> Optional[str]:
    m = model_name.lower()
    if "opus" in m: return "opus"
    if "sonnet" in m: return "sonnet"
    if "haiku" in m: return "haiku"
    return None


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_config(data: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    existing = load_config()
    existing.update(data)
    with open(CONFIG_PATH, "w") as f:
        json.dump(existing, f, indent=2)


def parse_args():
    cfg = load_config()
    p = argparse.ArgumentParser(
        description="Claude Max subscription usage calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s "2026-02-09 14:00"                # Basic usage
  %(prog)s "2026-02-09 14:00" --save         # Save reset time & plan
  %(prog)s                                    # Use saved config
  %(prog)s --session main                     # Single session detail
  %(prog)s --top 5                            # Top 5 sessions only
  %(prog)s --json                             # JSON output
  %(prog)s --plan 20x                         # Override plan""")

    p.add_argument("reset_time", nargs="?", default=cfg.get("reset_time"),
                   help="Weekly reset time, e.g. '2026-02-09 15:00' (saved if --save)")
    p.add_argument("--plan", default=cfg.get("plan", "5x"),
                   choices=["pro", "5x", "20x"],
                   help=f"Subscription plan (default: {cfg.get('plan', '5x')})")
    p.add_argument("--tz", default=cfg.get("tz", "Australia/Melbourne"),
                   help=f"Timezone (default: {cfg.get('tz', 'Australia/Melbourne')})")
    p.add_argument("--sessions-dir", default=None,
                   help="Path to sessions dir (auto-detected)")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--top", type=int, default=0,
                   help="Show top N sessions (0 = all)")
    p.add_argument("--session", default=None,
                   help="Detail for a specific session (substring match)")
    p.add_argument("--save", action="store_true",
                   help="Save reset_time, plan, and tz to config")
    p.add_argument("--reset-day", default=cfg.get("reset_day"),
                   help="Day of week for reset (e.g. 'monday'). Auto-calculates reset_time.")

    args = p.parse_args()

    # Auto-calculate reset_time from reset_day + time pattern
    if not args.reset_time and args.reset_day:
        args.reset_time = calc_reset_time(args.reset_day, cfg.get("reset_hour", "14:00"), args.tz)

    if not args.reset_time:
        p.error("reset_time required (provide as argument, use --save to remember, or set --reset-day)")

    if args.save:
        save_config({
            "reset_time": args.reset_time,
            "plan": args.plan,
            "tz": args.tz,
        })
        print(f"  ✓ Config saved to {CONFIG_PATH}")

    return args


def calc_reset_time(day_name: str, hour: str, tz_name: str) -> str:
    """Calculate the most recent reset time for the given day of week."""
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    days = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6}
    target_day = days.get(day_name.lower(), 0)
    h, m = map(int, hour.split(":"))

    # Find most recent occurrence of that day
    delta = (now.weekday() - target_day) % 7
    reset_date = now - timedelta(days=delta)
    reset_dt = reset_date.replace(hour=h, minute=m, second=0, microsecond=0)

    # If the calculated time is in the future, go back a week
    if reset_dt > now:
        reset_dt -= timedelta(days=7)

    return reset_dt.strftime("%Y-%m-%d %H:%M")


def find_sessions_dir():
    candidates = [
        os.path.expanduser("~/.openclaw/agents/main/sessions"),
        os.path.expanduser("~/.moltbot/agents/main/sessions"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return None


def parse_reset_time(time_str: str, tz_name: str) -> datetime:
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tz_name)
    except ImportError:
        import subprocess
        offset = subprocess.check_output(["date", "+%z"]).decode().strip()
        h, m = int(offset[:3]), int(offset[0] + offset[3:5])
        tz = timezone(timedelta(hours=h, minutes=m))

    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    dt = dt.replace(tzinfo=tz)
    return dt.astimezone(timezone.utc)


def load_session_keys(sessions_dir: str) -> dict:
    mapping = {}
    sfile = os.path.join(sessions_dir, "sessions.json")
    if os.path.exists(sfile):
        with open(sfile) as f:
            data = json.load(f)
        for key, info in data.items():
            sid = info.get("sessionId", "")
            if sid:
                mapping[sid] = key
    return mapping


def scan_sessions(sessions_dir: str, since_utc: datetime):
    """Scan JSONL files and aggregate usage since reset time."""
    since_ms = int(since_utc.timestamp() * 1000)
    results = {}
    key_map = load_session_keys(sessions_dir)

    for fpath in glob.glob(os.path.join(sessions_dir, "*.jsonl")):
        fname = os.path.basename(fpath)
        session_id = fname.replace(".jsonl", "")
        session_key = key_map.get(session_id, session_id[:12])

        session_data = {
            "file": fname,
            "key": session_key,
            "models": {},
            "total_credits": 0,
            "total_input": 0,
            "total_output": 0,
            "total_cache_read": 0,
            "total_cache_write": 0,
            "turns": 0,
            "timestamps": [],  # for 5h window calc
        }

        with open(fpath) as f:
            for line in f:
                try:
                    msg = json.loads(line)
                except:
                    continue

                if msg.get("type") != "message":
                    continue

                m = msg.get("message", {})
                if m.get("role") != "assistant":
                    continue

                usage = m.get("usage")
                if not usage:
                    continue

                ts_str = msg.get("timestamp", "")
                if isinstance(ts_str, str):
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        ts_ms = int(ts.timestamp() * 1000)
                    except:
                        continue
                elif isinstance(ts_str, (int, float)):
                    ts_ms = int(ts_str)
                else:
                    continue

                if ts_ms < since_ms:
                    continue

                model = m.get("model", "unknown")
                tier = get_tier(model)

                inp = usage.get("input", 0)
                out = usage.get("output", 0)
                cr = usage.get("cacheRead", 0)
                cw = usage.get("cacheWrite", 0)

                credits = 0
                if tier and tier in CREDIT_RATES:
                    rates = CREDIT_RATES[tier]
                    credits = (inp + cw) * rates["input"] + out * rates["output"]

                if model not in session_data["models"]:
                    session_data["models"][model] = {
                        "tier": tier, "turns": 0, "input": 0, "output": 0,
                        "cache_read": 0, "cache_write": 0, "credits": 0,
                    }

                md = session_data["models"][model]
                md["turns"] += 1
                md["input"] += inp
                md["output"] += out
                md["cache_read"] += cr
                md["cache_write"] += cw
                md["credits"] += credits

                session_data["total_credits"] += credits
                session_data["total_input"] += inp
                session_data["total_output"] += out
                session_data["total_cache_read"] += cr
                session_data["total_cache_write"] += cw
                session_data["turns"] += 1
                session_data["timestamps"].append({"ts_ms": ts_ms, "credits": credits})

        if session_data["turns"] > 0:
            results[fname] = session_data

    return results


def calc_5h_window(results: dict) -> float:
    """Calculate credits consumed in the last 5 hours (sliding window)."""
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    window_ms = 5 * 3600 * 1000
    cutoff = now_ms - window_ms
    total = 0
    for s in results.values():
        for entry in s.get("timestamps", []):
            if entry["ts_ms"] >= cutoff:
                total += entry["credits"]
    return total


def format_session_detail(results: dict, plan_name: str, session_filter: str, as_json: bool = False):
    plan = PLANS[plan_name]
    weekly_budget = plan["per_week"]

    matches = []
    for fname, s in results.items():
        sid = fname.replace(".jsonl", "")
        if session_filter.lower() in s["key"].lower() or session_filter.lower() in sid.lower():
            matches.append((fname, s))

    if not matches:
        print(f"  No sessions matching '{session_filter}' found in this period.")
        return

    total_all = sum(s["total_credits"] for s in results.values())

    for fname, s in matches:
        sid = fname.replace(".jsonl", "")
        pct_week = s["total_credits"] / weekly_budget * 100 if weekly_budget else 0
        pct_total = s["total_credits"] / total_all * 100 if total_all else 0

        if as_json:
            print(json.dumps({
                "session_key": s["key"],
                "session_id": sid,
                "credits": round(s["total_credits"]),
                "pct_of_week": round(pct_week, 2),
                "pct_of_total_usage": round(pct_total, 2),
                "turns": s["turns"],
                "total_input": s["total_input"],
                "total_output": s["total_output"],
                "total_cache_read": s["total_cache_read"],
                "models": {m: {
                    "credits": round(d["credits"]),
                    "turns": d["turns"],
                    "input": d["input"],
                    "output": d["output"],
                    "cache_read": d["cache_read"],
                } for m, d in s["models"].items()},
            }, indent=2))
            continue

        print(f"  Session: {s['key']}")
        print(f"  ID:      {sid}")
        print(f"  Credits: {s['total_credits']:>12,.0f}")
        print(f"  % of weekly budget: {pct_week:.2f}%")
        print(f"  % of total usage:   {pct_total:.2f}%")
        print(f"  Turns:   {s['turns']}")
        print(f"  Input tokens:  {s['total_input']:>12,}")
        print(f"  Output tokens: {s['total_output']:>12,}")
        print(f"  Cache reads:   {s['total_cache_read']:>12,}")
        print()
        print(f"  Model breakdown:")
        for model, d in sorted(s["models"].items(), key=lambda x: -x[1]["credits"]):
            tier = get_tier(model)
            tag = f" [{tier}]" if tier else " [non-claude]"
            print(f"    {model}{tag}: {d['credits']:,.0f} credits | {d['turns']} turns | in:{d['input']:,} out:{d['output']:,} cache:{d['cache_read']:,}")
        print()


def format_output(results: dict, plan_name: str, reset_time: str, as_json: bool = False, top: int = 0):
    plan = PLANS[plan_name]
    weekly_budget = plan["per_week"]
    hourly_budget = plan["per_5h"]

    total_credits = sum(s["total_credits"] for s in results.values())
    total_turns = sum(s["turns"] for s in results.values())

    # 5h sliding window
    credits_5h = calc_5h_window(results)
    pct_5h = credits_5h / hourly_budget * 100 if hourly_budget else 0

    if as_json:
        output = {
            "plan": plan_name,
            "reset_time": reset_time,
            "weekly_budget": weekly_budget,
            "hourly_budget_5h": hourly_budget,
            "total_credits": round(total_credits),
            "weekly_pct": round(total_credits / weekly_budget * 100, 2),
            "credits_5h": round(credits_5h),
            "pct_5h": round(pct_5h, 2),
            "total_turns": total_turns,
            "sessions": {},
        }
        for fname, s in sorted(results.items(), key=lambda x: -x[1]["total_credits"]):
            output["sessions"][s["key"]] = {
                "sessionId": fname.replace(".jsonl", ""),
                "credits": round(s["total_credits"]),
                "pct": round(s["total_credits"] / weekly_budget * 100, 2),
                "turns": s["turns"],
                "models": {m: {
                    "credits": round(d["credits"]),
                    "turns": d["turns"],
                    "input": d["input"],
                    "output": d["output"],
                } for m, d in s["models"].items()},
            }
        print(json.dumps(output, indent=2))
        return

    pct = total_credits / weekly_budget * 100
    remain = weekly_budget - total_credits

    print(f"╔══════════════════════════════════════════════════════╗")
    print(f"║  Claude Max {plan_name.upper()} Usage Report                  ║")
    print(f"╠══════════════════════════════════════════════════════╣")
    print(f"║  Reset:  {reset_time:<42s} ║")
    print(f"║  Budget: {weekly_budget:>12,} credits/week                ║")
    print(f"║  Used:   {total_credits:>12,.0f} credits ({pct:.1f}%)             ║")
    print(f"║  Remain: {remain:>12,.0f} credits                     ║")
    print(f"║  Turns:  {total_turns:>12,}                             ║")
    print(f"╠──────────────────────────────────────────────────────╣")
    print(f"║  5h window: {credits_5h:>10,.0f} / {hourly_budget:>10,} ({pct_5h:.1f}%)", end="")

    # Rate limit warning
    if pct_5h > 80:
        print(f"  ⚠️ SLOW DOWN ║")
    elif pct_5h > 50:
        print(f"  ⚡ Watch it  ║")
    else:
        print(f"             ║")

    print(f"╚══════════════════════════════════════════════════════╝")
    print()

    # Progress bars
    bar_width = 40
    filled_w = int(bar_width * min(pct / 100, 1.0))
    bar_w = "█" * filled_w + "░" * (bar_width - filled_w)
    filled_h = int(bar_width * min(pct_5h / 100, 1.0))
    bar_h = "█" * filled_h + "░" * (bar_width - filled_h)
    print(f"  Weekly: [{bar_w}] {pct:.1f}%")
    print(f"  5h:     [{bar_h}] {pct_5h:.1f}%")
    print()

    # Per-session breakdown
    sorted_sessions = sorted(results.items(), key=lambda x: (-x[1]["total_credits"], -x[1]["turns"]))
    top_n = top if top > 0 else len(sorted_sessions)
    shown = sorted_sessions[:top_n]

    print(f"  Sessions (by credits):")
    print(f"  {'#':<3} {'Session':<48} {'Credits':>10} {'%':>7} {'Turns':>6}")
    print(f"  {'─'*3} {'─'*48} {'─'*10} {'─'*7} {'─'*6}")

    for i, (fname, s) in enumerate(shown, 1):
        label = s["key"][:48]
        models = ", ".join(s["models"].keys())
        if s["total_credits"] == 0:
            print(f"  {i:<3} {label:<48} {'(free)':>10} {'':>7} {s['turns']:>6}  [{models}]")
        else:
            spct = s["total_credits"] / weekly_budget * 100
            print(f"  {i:<3} {label:<48} {s['total_credits']:>10,.0f} {spct:>6.2f}% {s['turns']:>6}  [{models}]")

    if len(sorted_sessions) > top_n:
        remaining = len(sorted_sessions) - top_n
        remaining_credits = sum(s["total_credits"] for _, s in sorted_sessions[top_n:])
        print(f"  ... and {remaining} more sessions ({remaining_credits:,.0f} credits)")

    print()

    # Model summary
    model_totals = {}
    for s in results.values():
        for model, d in s["models"].items():
            if model not in model_totals:
                model_totals[model] = {"credits": 0, "turns": 0, "input": 0, "output": 0, "cache_read": 0}
            model_totals[model]["credits"] += d["credits"]
            model_totals[model]["turns"] += d["turns"]
            model_totals[model]["input"] += d["input"]
            model_totals[model]["output"] += d["output"]
            model_totals[model]["cache_read"] += d["cache_read"]

    print(f"  Model breakdown:")
    for model, d in sorted(model_totals.items(), key=lambda x: -x[1]["credits"]):
        tier = get_tier(model)
        tag = f" [{tier}]" if tier else " [non-claude]"
        mpct = d["credits"] / weekly_budget * 100 if d["credits"] > 0 else 0
        print(f"    {model}{tag}: {d['credits']:,.0f} credits ({mpct:.2f}%) | {d['turns']} turns | {d['cache_read']:,} cache reads")


def main():
    args = parse_args()

    sessions_dir = args.sessions_dir or find_sessions_dir()
    if not sessions_dir or not os.path.isdir(sessions_dir):
        print("Error: Sessions directory not found. Use --sessions-dir to specify.", file=sys.stderr)
        sys.exit(1)

    reset_utc = parse_reset_time(args.reset_time, args.tz)
    results = scan_sessions(sessions_dir, reset_utc)

    if args.session:
        format_session_detail(results, args.plan, args.session, args.json)
    else:
        format_output(results, args.plan, args.reset_time, args.json, args.top)


if __name__ == "__main__":
    main()
