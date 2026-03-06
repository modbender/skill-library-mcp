#!/usr/bin/env python3
"""
OpenRouter analytics + troubleshooting helper.

Supports:
- activity (management key)
- credits (management key)
- keys (management key)
- generation (regular API key)
- report (management key; combines activity+credits+keys)

Environment variables:
- OPENROUTER_MANAGEMENT_KEY
- OPENROUTER_API_KEY

Also attempts to auto-load ~/.openclaw/.env if variables are not already set.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional

BASE_URL = "https://openrouter.ai/api/v1"


def load_dotenv(path: str) -> None:
    """Minimal .env loader (KEY=VALUE, ignores comments/blank lines)."""
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except OSError:
        pass


class ORClient:
    def __init__(self, token: str, timeout: int = 30, retries: int = 2, retry_delay: float = 0.6):
        self.token = token
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay

    def request(self, method: str, path: str, query: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{BASE_URL}{path}"
        if query:
            url += "?" + urllib.parse.urlencode({k: v for k, v in query.items() if v is not None})

        req = urllib.request.Request(
            url,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
        )

        last_err: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
                # Retry transient statuses only
                if e.code in (408, 429, 500, 502, 503, 504) and attempt < self.retries:
                    time.sleep(self.retry_delay * (attempt + 1))
                    last_err = RuntimeError(f"HTTP {e.code}: {body}")
                    continue
                raise RuntimeError(f"HTTP {e.code}: {body}") from e
            except urllib.error.URLError as e:
                if attempt < self.retries:
                    time.sleep(self.retry_delay * (attempt + 1))
                    last_err = RuntimeError(f"Network error: {e.reason}")
                    continue
                raise RuntimeError(f"Network error: {e.reason}") from e

        raise RuntimeError(str(last_err or "Unknown request error"))


def get_token(explicit: Optional[str], env_name: str) -> str:
    token = explicit or os.getenv(env_name)
    if not token:
        raise RuntimeError(f"Missing token. Provide --token or set {env_name}.")
    return token


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def parse_date(value: str) -> dt.date:
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as e:
        raise RuntimeError(f"Invalid date '{value}'. Use YYYY-MM-DD.") from e


def date_range(start: dt.date, end: dt.date) -> Iterable[dt.date]:
    cur = start
    while cur <= end:
        yield cur
        cur += dt.timedelta(days=1)


def fetch_activity_range(client: ORClient, from_date: str, to_date: str) -> List[Dict[str, Any]]:
    start = parse_date(from_date)
    end = parse_date(to_date)
    if end < start:
        raise RuntimeError("--to must be >= --from")

    rows: List[Dict[str, Any]] = []
    for d in date_range(start, end):
        payload = client.request("GET", "/activity", query={"date": d.isoformat()})
        rows.extend(payload.get("data", []))
    return rows


def summarize_activity(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_model_cost: Dict[str, float] = defaultdict(float)
    by_provider_cost: Dict[str, float] = defaultdict(float)
    total_usage = 0.0
    total_requests = 0.0
    total_prompt_tokens = 0.0
    total_completion_tokens = 0.0
    total_reasoning_tokens = 0.0

    for row in items:
        usage = float(row.get("usage") or 0)
        reqs = float(row.get("requests") or 0)
        model = str(row.get("model") or "unknown")
        provider = str(row.get("provider_name") or "unknown")

        total_usage += usage
        total_requests += reqs
        total_prompt_tokens += float(row.get("prompt_tokens") or 0)
        total_completion_tokens += float(row.get("completion_tokens") or 0)
        total_reasoning_tokens += float(row.get("reasoning_tokens") or 0)

        by_model_cost[model] += usage
        by_provider_cost[provider] += usage

    top_models = sorted(by_model_cost.items(), key=lambda x: x[1], reverse=True)[:10]
    top_providers = sorted(by_provider_cost.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "rows": len(items),
        "total_usage_usd": total_usage,
        "total_requests": total_requests,
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "total_reasoning_tokens": total_reasoning_tokens,
        "top_models": top_models,
        "top_providers": top_providers,
    }


def maybe_write_activity_csv(path: Optional[str], items: List[Dict[str, Any]]) -> None:
    if not path:
        return
    fields = [
        "date",
        "model",
        "model_permaslug",
        "endpoint_id",
        "provider_name",
        "usage",
        "byok_usage_inference",
        "requests",
        "prompt_tokens",
        "completion_tokens",
        "reasoning_tokens",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in items:
            w.writerow({k: row.get(k) for k in fields})


def cmd_activity(args: argparse.Namespace) -> int:
    token = get_token(args.token, "OPENROUTER_MANAGEMENT_KEY")
    client = ORClient(token, timeout=args.timeout, retries=args.retries)

    if args.from_date and args.to_date:
        items = fetch_activity_range(client, args.from_date, args.to_date)
        data = {"data": items}
    elif args.date:
        data = client.request("GET", "/activity", query={"date": args.date})
        items = data.get("data", [])
    else:
        data = client.request("GET", "/activity")
        items = data.get("data", [])

    if args.raw:
        print_json(data)
        return 0

    maybe_write_activity_csv(args.csv, items)

    if args.summary:
        s = summarize_activity(items)
        print(f"Rows: {s['rows']}")
        print(f"Total usage (USD): {s['total_usage_usd']:.6f}")
        print(f"Total requests: {s['total_requests']:.0f}")
        print(
            f"Tokens prompt/completion/reasoning: "
            f"{s['total_prompt_tokens']:.0f}/{s['total_completion_tokens']:.0f}/{s['total_reasoning_tokens']:.0f}"
        )
        print("Top models by cost:")
        for model, cost in s["top_models"][: args.limit]:
            print(f"  - {model}: ${cost:.6f}")
        print("Top providers by cost:")
        for provider, cost in s["top_providers"][: args.limit]:
            print(f"  - {provider}: ${cost:.6f}")
        if args.csv:
            print(f"CSV exported: {args.csv}")
        return 0

    print(f"Activity rows: {len(items)}")
    if not items:
        return 0

    for row in items[: args.limit]:
        print(
            " | ".join(
                [
                    str(row.get("date", "")),
                    str(row.get("model", "")),
                    str(row.get("provider_name", "")),
                    f"requests={row.get('requests', 0)}",
                    f"usage=${row.get('usage', 0)}",
                ]
            )
        )

    if args.csv:
        print(f"CSV exported: {args.csv}")
    return 0


def cmd_credits(args: argparse.Namespace) -> int:
    token = get_token(args.token, "OPENROUTER_MANAGEMENT_KEY")
    client = ORClient(token, timeout=args.timeout, retries=args.retries)
    data = client.request("GET", "/credits")

    if args.raw:
        print_json(data)
        return 0

    d = data.get("data", {})
    total = float(d.get("total_credits", 0) or 0)
    used = float(d.get("total_usage", 0) or 0)
    remaining = total - used
    pct = (used / total * 100.0) if total > 0 else 0
    print(f"Total credits: {total:.6f}")
    print(f"Used: {used:.6f}")
    print(f"Remaining: {remaining:.6f}")
    print(f"Used %: {pct:.2f}%")
    return 0


def cmd_keys(args: argparse.Namespace) -> int:
    token = get_token(args.token, "OPENROUTER_MANAGEMENT_KEY")
    client = ORClient(token, timeout=args.timeout, retries=args.retries)
    data = client.request("GET", "/keys", query={"offset": str(args.offset)})

    if args.raw:
        print_json(data)
        return 0

    keys = data.get("data", [])
    print(f"Keys returned: {len(keys)}")
    if args.summary:
        total_usage = sum(float(k.get("usage") or 0) for k in keys)
        total_daily = sum(float(k.get("usage_daily") or 0) for k in keys)
        total_weekly = sum(float(k.get("usage_weekly") or 0) for k in keys)
        total_monthly = sum(float(k.get("usage_monthly") or 0) for k in keys)
        print(f"Aggregate usage: ${total_usage:.6f}")
        print(f"Aggregate daily: ${total_daily:.6f}")
        print(f"Aggregate weekly: ${total_weekly:.6f}")
        print(f"Aggregate monthly: ${total_monthly:.6f}")

    for row in keys[: args.limit]:
        print(
            " | ".join(
                [
                    str(row.get("name", "(unnamed)")),
                    str(row.get("label", "")),
                    f"disabled={row.get('disabled', False)}",
                    f"usage=${row.get('usage', 0)}",
                    f"daily=${row.get('usage_daily', 0)}",
                    f"weekly=${row.get('usage_weekly', 0)}",
                    f"monthly=${row.get('usage_monthly', 0)}",
                ]
            )
        )
    return 0


def cmd_generation(args: argparse.Namespace) -> int:
    token = get_token(args.token, "OPENROUTER_API_KEY")
    client = ORClient(token, timeout=args.timeout, retries=args.retries)
    data = client.request("GET", "/generation", query={"id": args.id})

    if args.raw:
        print_json(data)
        return 0

    d = data.get("data", {})
    print(f"id: {d.get('id')}")
    print(f"model: {d.get('model')}")
    print(f"provider: {d.get('provider_name')}")
    print(f"usage_usd: {d.get('usage')}")
    print(f"total_cost_usd: {d.get('total_cost')}")
    print(f"upstream_inference_cost_usd: {d.get('upstream_inference_cost')}")
    print(f"tokens_prompt: {d.get('tokens_prompt')}")
    print(f"tokens_completion: {d.get('tokens_completion')}")
    print(f"native_cached_tokens: {d.get('native_tokens_cached')}")
    print(f"reasoning_tokens: {d.get('native_tokens_reasoning')}")
    print(f"finish_reason: {d.get('finish_reason')}")
    print(f"native_finish_reason: {d.get('native_finish_reason')}")
    print(f"latency_ms: {d.get('latency')}")
    print(f"generation_time_ms: {d.get('generation_time')}")

    provider_responses = d.get("provider_responses") or []
    if provider_responses:
        print("provider_responses:")
        for pr in provider_responses:
            print(
                "  - "
                + " | ".join(
                    [
                        f"provider={pr.get('provider_name')}",
                        f"endpoint_id={pr.get('endpoint_id')}",
                        f"status={pr.get('status')}",
                        f"latency={pr.get('latency')}",
                        f"byok={pr.get('is_byok')}",
                    ]
                )
            )
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    token = get_token(args.token, "OPENROUTER_MANAGEMENT_KEY")
    client = ORClient(token, timeout=args.timeout, retries=args.retries)

    # Activity window
    if args.from_date and args.to_date:
        activity_items = fetch_activity_range(client, args.from_date, args.to_date)
        report_range = f"{args.from_date}..{args.to_date}"
    elif args.date:
        payload = client.request("GET", "/activity", query={"date": args.date})
        activity_items = payload.get("data", [])
        report_range = args.date
    else:
        payload = client.request("GET", "/activity")
        activity_items = payload.get("data", [])
        report_range = "last 30 completed UTC days"

    credits = client.request("GET", "/credits").get("data", {})
    keys = client.request("GET", "/keys").get("data", [])

    summary = summarize_activity(activity_items)
    key_top = sorted(keys, key=lambda k: float(k.get("usage") or 0), reverse=True)[: args.limit]

    output = {
        "range": report_range,
        "activity_summary": summary,
        "credits": credits,
        "top_keys_by_usage": [
            {
                "name": k.get("name"),
                "label": k.get("label"),
                "disabled": k.get("disabled"),
                "usage": k.get("usage"),
                "usage_daily": k.get("usage_daily"),
                "usage_weekly": k.get("usage_weekly"),
                "usage_monthly": k.get("usage_monthly"),
            }
            for k in key_top
        ],
    }

    if args.raw:
        print_json(output)
        return 0

    if args.format == "json":
        print_json(output)
        return 0

    # Markdown default
    print(f"# OpenRouter Usage Report ({report_range})")
    print()
    print("## Credits")
    total = float(credits.get("total_credits", 0) or 0)
    used = float(credits.get("total_usage", 0) or 0)
    remaining = total - used
    print(f"- Total credits: `{total:.6f}`")
    print(f"- Used: `{used:.6f}`")
    print(f"- Remaining: `{remaining:.6f}`")
    print()

    print("## Activity Summary")
    print(f"- Rows: `{summary['rows']}`")
    print(f"- Total usage (USD): `${summary['total_usage_usd']:.6f}`")
    print(f"- Total requests: `{summary['total_requests']:.0f}`")
    print(
        "- Tokens prompt/completion/reasoning: "
        f"`{summary['total_prompt_tokens']:.0f}/{summary['total_completion_tokens']:.0f}/{summary['total_reasoning_tokens']:.0f}`"
    )
    print()

    print("### Top Models by Cost")
    for model, cost in summary["top_models"][: args.limit]:
        print(f"- `{model}`: `${cost:.6f}`")
    print()

    print("### Top Providers by Cost")
    for provider, cost in summary["top_providers"][: args.limit]:
        print(f"- `{provider}`: `${cost:.6f}`")
    print()

    print("## Top API Keys by Usage")
    if not key_top:
        print("- No keys returned")
    for k in key_top:
        print(
            f"- `{k.get('name') or '(unnamed)'}` ({k.get('label') or 'no-label'}) "
            f"usage=`${float(k.get('usage') or 0):.6f}` daily=`${float(k.get('usage_daily') or 0):.6f}` "
            f"weekly=`${float(k.get('usage_weekly') or 0):.6f}` monthly=`${float(k.get('usage_monthly') or 0):.6f}` "
            f"disabled=`{k.get('disabled')}`"
        )

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="OpenRouter analytics and troubleshooting helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--token", help="Override auth token")
    common.add_argument("--timeout", type=int, default=30)
    common.add_argument("--retries", type=int, default=2)
    common.add_argument("--raw", action="store_true", help="Print full JSON response")

    a = sub.add_parser("activity", parents=[common], help="Get activity (management key)")
    a.add_argument("--date", help="UTC date YYYY-MM-DD")
    a.add_argument("--from", dest="from_date", help="UTC start date YYYY-MM-DD")
    a.add_argument("--to", dest="to_date", help="UTC end date YYYY-MM-DD")
    a.add_argument("--limit", type=int, default=20)
    a.add_argument("--summary", action="store_true", help="Show aggregate totals and top model/provider cost")
    a.add_argument("--csv", help="Export activity rows to CSV file")
    a.set_defaults(func=cmd_activity)

    c = sub.add_parser("credits", parents=[common], help="Get credits usage (management key)")
    c.set_defaults(func=cmd_credits)

    k = sub.add_parser("keys", parents=[common], help="List key usage stats (management key)")
    k.add_argument("--offset", type=int, default=0)
    k.add_argument("--limit", type=int, default=20)
    k.add_argument("--summary", action="store_true", help="Show aggregate usage totals")
    k.set_defaults(func=cmd_keys)

    g = sub.add_parser("generation", parents=[common], help="Inspect one generation id (regular key)")
    g.add_argument("--id", required=True, help="Generation ID from completion response")
    g.set_defaults(func=cmd_generation)

    r = sub.add_parser("report", parents=[common], help="Build consolidated management report")
    r.add_argument("--date", help="UTC date YYYY-MM-DD")
    r.add_argument("--from", dest="from_date", help="UTC start date YYYY-MM-DD")
    r.add_argument("--to", dest="to_date", help="UTC end date YYYY-MM-DD")
    r.add_argument("--limit", type=int, default=10, help="Top-N models/providers/keys")
    r.add_argument("--format", choices=["markdown", "json"], default="markdown")
    r.set_defaults(func=cmd_report)

    return p


def main() -> int:
    # Auto-load .env hints before parsing/executing commands
    load_dotenv(os.path.expanduser("~/.openclaw/.env"))
    load_dotenv(os.path.join(os.getcwd(), ".env"))

    parser = build_parser()
    args = parser.parse_args()

    # Simple argument guardrails
    if getattr(args, "from_date", None) and not getattr(args, "to_date", None):
        print("ERROR: --from requires --to", file=sys.stderr)
        return 1
    if getattr(args, "to_date", None) and not getattr(args, "from_date", None):
        print("ERROR: --to requires --from", file=sys.stderr)
        return 1

    try:
        return args.func(args)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
