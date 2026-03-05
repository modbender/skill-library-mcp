#!/usr/bin/env python3
"""
Read-only Umami API query helper.

Examples:
  python3 scripts/umami_query.py --endpoint /v1/websites
  python3 scripts/umami_query.py --endpoint /v1/websites/{websiteId}/stats --preset last7d
  python3 scripts/umami_query.py --endpoint /v1/websites/{websiteId}/pageviews --preset last30d
  python3 scripts/umami_query.py --endpoint /v1/websites/{websiteId}/events --param eventName=signup
"""

import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request


DEFAULT_BASE_URL = "https://api.umami.is"


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def ms(ts: dt.datetime) -> int:
    return int(ts.timestamp() * 1000)


def start_of_day(x: dt.datetime) -> dt.datetime:
    return x.replace(hour=0, minute=0, second=0, microsecond=0)


def start_of_month(x: dt.datetime) -> dt.datetime:
    return x.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def end_of_month(x: dt.datetime) -> dt.datetime:
    if x.month == 12:
        nxt = x.replace(year=x.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        nxt = x.replace(month=x.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return nxt - dt.timedelta(milliseconds=1)


def preset_range(preset: str):
    now = utc_now()
    today = start_of_day(now)

    if preset == "today":
        return ms(today), ms(now)
    if preset == "yesterday":
        y0 = today - dt.timedelta(days=1)
        y1 = today - dt.timedelta(milliseconds=1)
        return ms(y0), ms(y1)
    if preset == "last24h":
        return ms(now - dt.timedelta(hours=24)), ms(now)
    if preset == "last7d":
        return ms(now - dt.timedelta(days=7)), ms(now)
    if preset == "last30d":
        return ms(now - dt.timedelta(days=30)), ms(now)
    if preset == "monthToDate":
        m0 = start_of_month(now)
        return ms(m0), ms(now)
    if preset == "previousMonth":
        this_month = start_of_month(now)
        prev_last = this_month - dt.timedelta(milliseconds=1)
        prev_first = start_of_month(prev_last)
        return ms(prev_first), ms(prev_last)
    if preset == "yearToDate":
        y0 = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return ms(y0), ms(now)

    raise ValueError(f"Unknown preset: {preset}")


def parse_kv(items):
    out = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid --param '{item}'. Use key=value.")
        k, v = item.split("=", 1)
        out[k] = v
    return out


def replace_tokens(endpoint: str, website_id: str, path_vars: dict):
    merged = dict(path_vars)
    if website_id:
        merged.setdefault("websiteId", website_id)

    result = endpoint
    for k, v in merged.items():
        result = result.replace("{" + k + "}", str(v))

    if "{" in result and "}" in result:
        raise ValueError(
            f"Unresolved path variables in endpoint: {result}. "
            "Pass --website-id or --path-var key=value"
        )

    return result


def normalize_endpoint(endpoint: str, deployment: str) -> str:
    path = endpoint if endpoint.startswith("/") else "/" + endpoint
    if deployment == "cloud":
        # Umami Cloud analytics API uses /v1 paths.
        if path.startswith("/api/"):
            return "/v1/" + path[len("/api/"):]
        return path

    # Self-hosted Umami uses /api paths.
    if path.startswith("/v1/"):
        return "/api/" + path[len("/v1/"):]
    return path


def build_url(base_url: str, endpoint: str, params: dict, deployment: str):
    base = base_url.rstrip("/")
    path = normalize_endpoint(endpoint, deployment)
    if params:
        return f"{base}{path}?{urllib.parse.urlencode(params, doseq=True)}"
    return f"{base}{path}"


def apply_endpoint_defaults(endpoint: str, params: dict, website_id: str | None):
    """Apply practical defaults for common Umami endpoints."""
    path = endpoint

    # Metrics endpoints require `type` in Umami Cloud.
    if (path.endswith("/metrics") or "/metrics/expanded" in path) and "type" not in params:
        params["type"] = "url"

    # Report endpoints on /v1/reports/* usually require websiteId.
    if path.startswith("/v1/reports/") and path != "/v1/reports" and website_id:
        params.setdefault("websiteId", website_id)

    return params


def explain_http_error(endpoint: str, code: int, body: str, deployment: str) -> str:
    body_l = (body or "").lower()

    # Cloud restriction: user-scoped endpoints are often forbidden for normal user keys.
    if code == 403 and deployment == "cloud" and endpoint.startswith("/v1/users/"):
        return "Hint: /v1/users/* endpoints are often restricted on Umami Cloud for non-admin user API keys."

    # Common cause of 500 during manual probing: fake IDs.
    suspicious = ["missing-", "placeholder", "dummy", "invalid"]
    if code == 500 and any(s in endpoint for s in suspicious):
        return "Hint: This endpoint likely needs a real resource ID (teamId/sessionId/eventId/reportId), not a placeholder."

    # Missing metrics type shows as bad-request in cloud.
    if code == 400 and "/metrics" in endpoint and "type" in body_l and "invalid input" in body_l:
        return "Hint: metrics endpoints require `type` (e.g. --param type=url|referrer|browser|os|device|country|city)."

    return ""


def main():
    parser = argparse.ArgumentParser(description="Query Umami API (read-only GET)")
    parser.add_argument("--endpoint", required=True, help="Endpoint path, e.g. /v1/websites/{websiteId}/stats (legacy /api/... auto-maps to /v1/...) ")
    parser.add_argument("--base-url", default=os.getenv("UMAMI_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--api-key", default=os.getenv("UMAMI_API_KEY"))
    parser.add_argument("--website-id", default=os.getenv("UMAMI_WEBSITE_ID"))
    parser.add_argument(
        "--deployment",
        choices=["cloud", "self-hosted"],
        default=os.getenv("UMAMI_DEPLOYMENT", "cloud"),
        help="API path/auth mode. cloud => /v1 + x-umami-api-key, self-hosted => /api + Bearer token",
    )
    parser.add_argument("--path-var", action="append", default=[], help="Path variable replacement, key=value")
    parser.add_argument("--param", action="append", default=[], help="Query parameter, key=value")
    parser.add_argument(
        "--preset",
        choices=["today", "yesterday", "last24h", "last7d", "last30d", "monthToDate", "previousMonth", "yearToDate"],
        help="Apply a built-in time range (sets startAt/endAt unless already provided)",
    )
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--raw", action="store_true", help="Print raw response text")

    args = parser.parse_args()

    if not args.api_key:
        print("Missing API key. Set UMAMI_API_KEY or pass --api-key.", file=sys.stderr)
        sys.exit(2)

    try:
        path_vars = parse_kv(args.path_var)
        params = parse_kv(args.param)

        if args.preset:
            start_at, end_at = preset_range(args.preset)
            params.setdefault("startAt", str(start_at))
            params.setdefault("endAt", str(end_at))

        endpoint = replace_tokens(args.endpoint, args.website_id, path_vars)
        params = apply_endpoint_defaults(endpoint, params, args.website_id)
        url = build_url(args.base_url, endpoint, params, args.deployment)

        if args.deployment == "cloud":
            headers = {
                "Accept": "application/json",
                "x-umami-api-key": args.api_key,
                "User-Agent": "curl/8.5.0",
            }
        else:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {args.api_key}",
                "User-Agent": "curl/8.5.0",
            }

        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")

        if args.raw:
            print(body)
            return

        try:
            obj = json.loads(body)
            print(json.dumps(obj, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(body)

    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        if err_body:
            print(err_body, file=sys.stderr)

        hint = explain_http_error(endpoint=endpoint, code=e.code, body=err_body, deployment=args.deployment)
        if hint:
            print(hint, file=sys.stderr)

        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
