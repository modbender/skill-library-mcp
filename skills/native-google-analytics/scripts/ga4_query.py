#!/usr/bin/env python3
"""
GA4 query script — calls analyticsdata.googleapis.com directly.
No third-party proxy or managed OAuth.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

# ── Auth ─────────────────────────────────────────────────────────────────────

def get_access_token():
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN")

    missing = [k for k, v in {
        "GOOGLE_CLIENT_ID": client_id,
        "GOOGLE_CLIENT_SECRET": client_secret,
        "GOOGLE_REFRESH_TOKEN": refresh_token,
    }.items() if not v]

    if missing:
        print(f"Error: missing env vars: {', '.join(missing)}", file=sys.stderr)
        print("Run ga4_auth.py to complete setup.", file=sys.stderr)
        sys.exit(1)

    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())["access_token"]
    except urllib.error.HTTPError as e:
        print(f"Auth error: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


# ── API ───────────────────────────────────────────────────────────────────────

def run_report(property_id, metrics, dimensions, start, end, limit, filter_expr, access_token):
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport"

    body = {
        "dateRanges": [{"startDate": start, "endDate": end}],
        "metrics": [{"name": m.strip()} for m in metrics],
        "dimensions": [{"name": d.strip()} for d in dimensions],
        "limit": limit,
    }

    if filter_expr:
        # Simple dimension filter: "pagePath=~/blog/"
        # Supports: = (exact), =~ (regex), != (not exact), !~ (not regex)
        for op_str, op_name in [("=~", "PARTIAL_REGEXP"), ("!~", "NOT_PARTIAL_REGEXP"), ("!=", "EXACT"), ("=", "EXACT")]:
            if op_str in filter_expr:
                parts = filter_expr.split(op_str, 1)
                negate = op_name.startswith("NOT_")
                body["dimensionFilter"] = {
                    "filter": {
                        "fieldName": parts[0].strip(),
                        "stringFilter": {
                            "matchType": "PARTIAL_REGEXP" if "REGEXP" in op_name else "EXACT",
                            "value": parts[1].strip(),
                            "caseSensitive": False,
                        },
                    }
                }
                if negate:
                    body["dimensionFilter"] = {"notExpression": body["dimensionFilter"]}
                break

    payload = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error = e.read().decode()
        print(f"API error {e.code}: {error}", file=sys.stderr)
        sys.exit(1)


# ── Output ────────────────────────────────────────────────────────────────────

def print_table(response, dimensions, metrics):
    if not response.get("rows"):
        print("No data returned.")
        return

    headers = dimensions + metrics
    rows = []
    for row in response["rows"]:
        dim_vals = [v["value"] for v in row.get("dimensionValues", [])]
        metric_vals = [v["value"] for v in row.get("metricValues", [])]
        rows.append(dim_vals + metric_vals)

    # Column widths
    widths = [max(len(h), max((len(r[i]) for r in rows), default=0)) for i, h in enumerate(headers)]

    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header_row = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"

    print(sep)
    print(header_row)
    print(sep)
    for row in rows:
        print("| " + " | ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)) + " |")
    print(sep)

    total = response.get("rowCount", len(rows))
    print(f"\n{len(rows)} rows shown / {total} total")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Query GA4 via Analytics Data API")
    parser.add_argument("--metrics", required=True, help="Comma-separated metrics, e.g. screenPageViews,sessions")
    parser.add_argument("--metric", help="Single metric (alias for --metrics)")
    parser.add_argument("--dimensions", help="Comma-separated dimensions, e.g. pagePath,deviceCategory")
    parser.add_argument("--dimension", help="Single dimension (alias for --dimensions)")
    parser.add_argument("--start", default="30daysAgo", help="Start date (YYYY-MM-DD or NdaysAgo)")
    parser.add_argument("--end", default="today", help="End date (YYYY-MM-DD or today)")
    parser.add_argument("--limit", type=int, default=20, help="Max rows to return")
    parser.add_argument("--filter", dest="filter_expr", help='Dimension filter, e.g. "pagePath=~/blog/"')
    parser.add_argument("--property", help="GA4 property ID (overrides GA4_PROPERTY_ID env var)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of table")
    args = parser.parse_args()

    property_id = args.property or os.environ.get("GA4_PROPERTY_ID")
    if not property_id:
        print("Error: GA4_PROPERTY_ID env var not set (or use --property)", file=sys.stderr)
        sys.exit(1)

    # Normalize metric/dimension args
    metrics_str = args.metrics or args.metric
    dimensions_str = args.dimensions or args.dimension or ""
    metrics = [m.strip() for m in metrics_str.split(",") if m.strip()]
    dimensions = [d.strip() for d in dimensions_str.split(",") if d.strip()]

    if not metrics:
        print("Error: at least one metric required", file=sys.stderr)
        sys.exit(1)

    access_token = get_access_token()
    response = run_report(property_id, metrics, dimensions, args.start, args.end, args.limit, args.filter_expr, access_token)

    if args.json:
        print(json.dumps(response, indent=2))
    else:
        print_table(response, dimensions, metrics)


if __name__ == "__main__":
    main()
