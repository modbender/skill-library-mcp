#!/usr/bin/env python3
"""
TBOT / TradingBoat webhook JSON generator + sender (OpenClaw side).

Occam's razor version:
 - Build TBOT-compatible payload
 - Validate strictly against alert_webhook_schema.json
 - Fail fast if invalid

Behavior:
 - This command ALWAYS sends the generated, schema-validated JSON payload to TBOT.
 - Webhook endpoint is taken from (in order): --url, TBOT_WEBHOOK_URL, or defaults to http://127.0.0.1:5001/webhook.
 - Webhook key is taken from (in order): --key, WEBHOOK_KEY env var, or the runtime .env file (auto-discovered).
 - orderRef defaults to Close_<TICKER>_<QTY>_<epoch_ms> when omitted.
 - If --close <QTY> is provided, direction defaults to strategy.close and contract defaults to stock.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from hashlib import md5
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib import error, request

import jsonschema

# -------------------------------------------------------------------
# Schema (single source of truth)
# -------------------------------------------------------------------

SCHEMA_PATH = Path(__file__).parent / "schema" / "alert_webhook_schema.json"

# -------------------------------------------------------------------
# Runtime env discovery (.env)
# -------------------------------------------------------------------

_DEFAULT_WEBHOOK_URL = "http://127.0.0.1:5001/webhook"


def _parse_dotenv(path: Path) -> Dict[str, str]:
    """Minimal .env parser (KEY=VALUE, ignores comments/blank lines)."""
    out: Dict[str, str] = {}
    try:
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k:
                out[k] = v
    except FileNotFoundError:
        return {}
    return out


def _candidate_runtime_dirs() -> List[Path]:
    """Best-effort search order for the TBOT runtime folder."""
    cands: List[Path] = []

    # Explicit env
    for var in ("TBOT_COMPOSE_DIR", "COMPOSE_DIR"):
        val = os.getenv(var)
        if val:
            cands.append(Path(os.path.expanduser(val)))

    # Common OpenClaw workspace location
    home = Path.home()
    cands.append(home / ".openclaw" / "workspace" / "openclaw-on-tradingboat")

    # Current working directory and parents (useful when invoked from runtime)
    cwd = Path.cwd()
    cands.extend([cwd, cwd.parent, cwd.parent.parent])

    # De-dup while preserving order
    seen = set()
    out: List[Path] = []
    for p in cands:
        try:
            rp = p.resolve()
        except Exception:
            rp = p
        if rp in seen:
            continue
        seen.add(rp)
        out.append(p)
    return out


def _discover_runtime_env() -> Dict[str, str]:
    """Load the first .env we can find from candidate runtime dirs."""
    for d in _candidate_runtime_dirs():
        env_path = d / ".env"
        if env_path.exists() and env_path.is_file():
            return _parse_dotenv(env_path)
    return {}


def _resolve_webhook_url(cli_url: str) -> str:
    if cli_url:
        return cli_url
    env_url = os.getenv("TBOT_WEBHOOK_URL", "").strip()
    if env_url:
        return env_url
    return _DEFAULT_WEBHOOK_URL


def _resolve_webhook_key(cli_key: str) -> str:
    if cli_key:
        return cli_key
    env_key = os.getenv("WEBHOOK_KEY", "").strip()
    if env_key:
        return env_key

    dotenv = _discover_runtime_env()

    # Try common names used in runtime envs
    for k in ("WEBHOOK_KEY", "TBOT_WEBHOOK_KEY", "TVWB_KEY", "TV_WEBHOOK_KEY"):
        v = (dotenv.get(k) or "").strip()
        if v:
            return v

    # If no explicit key, generate from TVWB UNIQUE_KEY (env or .keyfile).
    unique_key = _resolve_unique_key(dotenv)
    if unique_key:
        return _generate_webhook_key(unique_key)

    # Fallback: any key-like var containing 'WEBHOOK' and 'KEY'
    for k, v in dotenv.items():
        if re.search(r"webhook", k, re.I) and re.search(r"key", k, re.I) and v.strip():
            return v.strip()

    return ""


def _resolve_unique_key(dotenv: Dict[str, str]) -> str:
    # Prefer explicit env var
    unique_key = os.getenv("TVWB_UNIQUE_KEY", "").strip()
    if unique_key:
        return unique_key

    # From runtime .env
    unique_key = (dotenv.get("TVWB_UNIQUE_KEY") or "").strip()
    if unique_key:
        return unique_key

    # From runtime .keyfile
    for d in _candidate_runtime_dirs():
        key_path = d / ".keyfile"
        if key_path.exists() and key_path.is_file():
            try:
                return key_path.read_text().strip()
            except Exception:
                continue
    return ""


def _generate_webhook_key(unique_key: str) -> str:
    # Must match TVWB event key format.
    digest = md5(f"WebhookReceived{unique_key}".encode()).hexdigest()[:6]
    return f"WebhookReceived:{digest}"


def _auto_order_ref(ticker: str, qty: int) -> str:
    return f"Close_{ticker}_{qty}_{int(time.time() * 1000)}"


def load_schema() -> Dict:
    if not SCHEMA_PATH.exists():
        raise SystemExit(f"Schema not found: {SCHEMA_PATH}")
    with SCHEMA_PATH.open() as f:
        return json.load(f)


def validate_schema(payload: Dict, schema: Dict) -> None:
    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError as e:
        raise SystemExit(f"Schema validation failed: {e.message}")


def post_json(url: str, payload: Dict[str, Any]) -> Tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, body
    except error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return e.code, body


# -------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------

def parse_number(s: str) -> Any:
    try:
        if any(c in s.lower() for c in (".", "e")):
            return float(s)
        return int(s)
    except Exception:
        return s


def parse_metric(kv: str) -> Tuple[str, Any]:
    if "=" not in kv:
        raise SystemExit(f"Invalid metric '{kv}', expected name=value")
    name, value = kv.split("=", 1)
    name = name.strip()
    if not name:
        raise SystemExit(f"Invalid metric '{kv}', empty name")
    return name, parse_number(value.strip())


# -------------------------------------------------------------------
# Payload builder
# -------------------------------------------------------------------

def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    metrics: List[Dict[str, Any]] = []

    # If --close is used, inject qty metric and default direction/contract.
    if args.close is not None:
        # ensure qty metric exists (do not duplicate)
        has_qty = any(m.startswith("qty=") for m in args.metric)
        if not has_qty:
            args.metric.append(f"qty={int(args.close)}")
        if not args.direction:
            args.direction = "strategy.close"
        if not args.contract:
            args.contract = "stock"

    for m in args.metric:
        k, v = parse_metric(m)
        metrics.append({"name": k, "value": v})

    # Minimal, schema-safe defaults
    if not metrics:
        metrics = [
            {"name": "entry.limit", "value": 0},
            {"name": "entry.stop", "value": 0},
            {"name": "exit.limit", "value": 0},
            {"name": "exit.stop", "value": 0},
            {"name": "qty", "value": 1},
            {"name": "price", "value": 0},
        ]

    # Auto-generate orderRef if omitted.
    if not args.orderRef:
        # Determine qty for ref (default 1 if not present)
        qty_val = 1
        for mm in metrics:
            if mm.get("name") == "qty":
                try:
                    qty_val = int(mm.get("value"))
                except Exception:
                    qty_val = 1
                break
        args.orderRef = _auto_order_ref(args.ticker, qty_val)

    # Default contract if still empty
    if not args.contract:
        args.contract = "stock"

    return {
        "timestamp": int(time.time() * 1000),
        "ticker": args.ticker,
        "timeframe": args.timeframe,
        "currency": args.currency,
        "clientId": args.clientId,
        "key": args.key,
        "orderRef": args.orderRef,
        "contract": args.contract,
        "direction": args.direction,
        "metrics": metrics,
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description="Generate schema-valid TBOT webhook JSON and send to TBOT webhook"
    )

    # Required by schema
    p.add_argument("--ticker", required=True)
    p.add_argument("--direction", default="")
    p.add_argument("--orderRef", default="")
    p.add_argument("--contract", default="")
    p.add_argument(
        "--close",
        type=int,
        default=None,
        help="Close position qty (sets strategy.close, contract stock, qty metric)",
    )

    # Defaults allowed by policy
    p.add_argument("--currency", default=os.getenv("DEFAULT_CURRENCY", "USD"))
    p.add_argument("--timeframe", default=os.getenv("DEFAULT_TIMEFRAME", "1D"))
    p.add_argument("--clientId", type=int, default=int(os.getenv("DEFAULT_CLIENT_ID", "1")))

    p.add_argument("--metric", action="append", default=[])
    p.add_argument("--key", default=os.getenv("WEBHOOK_KEY", ""))
    p.add_argument("-o", "--out", default="")
    p.add_argument("--url", default=os.getenv("TBOT_WEBHOOK_URL", ""), help="TBOT webhook URL (or set TBOT_WEBHOOK_URL)")

    args = p.parse_args()

    args.key = _resolve_webhook_key(args.key)
    if not args.key:
        raise SystemExit("Missing webhook key (set WEBHOOK_KEY or put it in the runtime .env)")

    schema = load_schema()
    payload = build_payload(args)

    # If user did not provide direction and did not use --close, assume close intent.
    if not args.direction:
        args.direction = "strategy.close"
        payload["direction"] = args.direction

    validate_schema(payload, schema)

    out = json.dumps(payload, indent=2)

    if args.out:
        Path(args.out).write_text(out + "\n")

    print(out)
    args.url = _resolve_webhook_url(args.url)
    if not args.url:
        raise SystemExit("Missing webhook URL (set TBOT_WEBHOOK_URL)")

    status_code, response_text = post_json(args.url, payload)
    print(f"SENT {status_code} {args.url}")
    if not (200 <= status_code <= 299):
        import sys
        print(f"ERROR response: {response_text}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
