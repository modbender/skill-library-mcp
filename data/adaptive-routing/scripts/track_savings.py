#!/usr/bin/env python3
"""Track token and cost savings from adaptive routing decisions.

Subcommands:
  log     --kind local_success|escalated|cloud|bypassed --tokens N --model MODEL
  summary
  reset

Outcome kinds:
  local_success  — routed locally, validation passed, no escalation
  escalated      — tried locally, validation failed, re-ran on cloud
  cloud          — routed straight to cloud (no local available / high complexity)
  bypassed       — adaptive routing bypassed (explicit override, etc.)

Data is persisted to ~/.openclaw/adaptive-routing/savings.json (schema v2).
Backward compat: --routed-to local|cloud is still accepted (maps to local_success|cloud).
"""
import argparse
import json
import os
from datetime import datetime, timezone

DB_PATH = os.path.expanduser("~/.openclaw/adaptive-routing/savings.json")

# Blended cost per 1K tokens (input + output average) for common cloud models
CLOUD_COSTS_PER_1K = {
    "gpt-4o": 0.005,
    "gpt-4o-mini": 0.000225,
    "claude-3-5-sonnet": 0.009,
    "claude-3-5-haiku": 0.001,
    "claude-3-opus": 0.045,
    "gemini-1.5-pro": 0.00175,
    "gemini-1.5-flash": 0.000125,
    "default": 0.005,
}

SCHEMA_VERSION = 2


def _empty_totals() -> dict:
    return {
        "local_success": 0,   # completed locally, no escalation
        "escalated": 0,       # tried local, failed validation, used cloud
        "cloud": 0,           # routed straight to cloud
        "bypassed": 0,        # adaptive routing bypassed
        "tokens_local": 0,    # tokens processed by local model
        "tokens_cloud": 0,    # tokens sent to cloud (escalated + direct cloud)
        "cost_saved_usd": 0.0,
    }


def _migrate_v1(db: dict) -> dict:
    """Migrate a v1 schema (local/cloud counts) to v2."""
    old = db.get("totals", {})
    new_totals = _empty_totals()
    new_totals["local_success"] = old.get("local", 0)
    new_totals["cloud"] = old.get("cloud", 0)
    new_totals["tokens_local"] = old.get("tokens_saved", 0)
    new_totals["cost_saved_usd"] = old.get("cost_saved_usd", 0.0)
    return {
        "version": SCHEMA_VERSION,
        "requests": db.get("requests", []),
        "totals": new_totals,
    }


def load_db() -> dict:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        with open(DB_PATH) as f:
            raw = json.load(f)
        if raw.get("version", 1) < SCHEMA_VERSION:
            return _migrate_v1(raw)
        # Merge in any missing v2 fields for forward-compat
        raw.setdefault("requests", [])
        merged = {**_empty_totals(), **raw.get("totals", {})}
        raw["totals"] = merged
        return raw
    return {
        "version": SCHEMA_VERSION,
        "requests": [],
        "totals": _empty_totals(),
    }


def save_db(db: dict) -> None:
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)


# ── CLI ───────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="cmd", required=True)

log_p = sub.add_parser("log", help="Record a routed request")
log_p.add_argument("--tokens", type=int, required=True, help="Token count for this request")
log_p.add_argument("--model", default="default", help="Cloud model that would have been used")
log_p.add_argument(
    "--kind",
    choices=["local_success", "escalated", "cloud", "bypassed"],
    default=None,
    help="Outcome kind (preferred)",
)
# Backward compat alias
log_p.add_argument(
    "--routed-to",
    choices=["local", "cloud"],
    default=None,
    dest="routed_to",
    help="Backward compat: use --kind instead",
)

sub.add_parser("summary", help="Print cumulative savings as JSON")
sub.add_parser("reset", help="Clear all saved data")

args = parser.parse_args()
db = load_db()

if args.cmd == "log":
    # Resolve kind: prefer --kind, fall back to --routed-to alias
    kind = args.kind
    if kind is None:
        if args.routed_to == "local":
            kind = "local_success"
        elif args.routed_to == "cloud":
            kind = "cloud"
        else:
            raise SystemExit("error: supply --kind or --routed-to")

    cost_per_k = CLOUD_COSTS_PER_1K.get(args.model, CLOUD_COSTS_PER_1K["default"])
    # Cost saved = tokens that ran locally instead of cloud (local_success only)
    cost_saved = (args.tokens / 1000) * cost_per_k if kind == "local_success" else 0.0

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tokens": args.tokens,
        "model": args.model,
        "kind": kind,
        "cost_saved_usd": round(cost_saved, 6),
    }
    db["requests"].append(entry)

    t = db["totals"]
    t[kind] = t.get(kind, 0) + 1
    if kind in ("local_success", "escalated"):
        t["tokens_local"] = t.get("tokens_local", 0) + args.tokens
    if kind in ("cloud", "escalated"):
        t["tokens_cloud"] = t.get("tokens_cloud", 0) + args.tokens
    if kind == "local_success":
        t["cost_saved_usd"] = round(t.get("cost_saved_usd", 0.0) + cost_saved, 6)

    save_db(db)
    print(json.dumps(entry))

elif args.cmd == "summary":
    t = db["totals"]
    runs_total = t["local_success"] + t["escalated"] + t["cloud"]
    pct_local = round(
        (t["local_success"] / runs_total * 100), 1
    ) if runs_total > 0 else 0.0
    escalation_rate = round(
        (t["escalated"] / (t["local_success"] + t["escalated"]) * 100), 1
    ) if (t["local_success"] + t["escalated"]) > 0 else 0.0

    print(json.dumps({
        "total_requests": runs_total,
        "local_success": t["local_success"],
        "escalated": t["escalated"],
        "cloud": t["cloud"],
        "bypassed": t.get("bypassed", 0),
        "pct_local": pct_local,
        "escalation_rate": escalation_rate,
        "tokens_local": t.get("tokens_local", 0),
        "tokens_cloud": t.get("tokens_cloud", 0),
        "cost_saved_usd": round(t.get("cost_saved_usd", 0.0), 4),
    }))

elif args.cmd == "reset":
    save_db({
        "version": SCHEMA_VERSION,
        "requests": [],
        "totals": _empty_totals(),
    })
    print(json.dumps({"reset": True, "db_path": DB_PATH}))
