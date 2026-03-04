# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Usage History

View detailed usage history with filtering and pagination.
Requires an Admin API key.
API docs: https://docs.venice.ai
"""

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

VENICE_BASE_URL = "https://api.venice.ai/api/v1"

VALID_CURRENCIES = ["DIEM", "USD", "VCU"]


def get_api_key() -> str:
    """Get Venice API key from environment."""
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is not set", file=sys.stderr)
        print("Get your ADMIN API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def get_usage(
    currency: str = "DIEM",
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
    page: int = 1,
    sort_order: str = "desc",
    output_format: str = "json",
    output_file: str | None = None,
) -> dict:
    """Get usage history."""
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    params: dict = {
        "currency": currency,
        "limit": min(limit, 200),
        "page": page,
        "sortOrder": sort_order,
    }

    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    print(f"Fetching {currency} usage (page {page}, limit {limit})...", file=sys.stderr)

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.get(
                f"{VENICE_BASE_URL}/billing/usage",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Print summary
            total = data.get("total", 0)
            results = data.get("data", [])
            pagination = data.get("pagination", {})
            
            print(f"\nFound {total} total records", file=sys.stderr)
            print(f"Showing {len(results)} records (page {page})", file=sys.stderr)
            
            if data.get("warning"):
                print(f"\n⚠️  {data['warning']}", file=sys.stderr)
            
            # Format output
            if output_format == "csv":
                output = format_csv(results)
            else:
                output = json.dumps(data, indent=2, default=str)
            
            # Save or print
            if output_file:
                output_path = Path(output_file).resolve()
                output_path.write_text(output)
                print(f"\nSaved to: {output_path}", file=sys.stderr)
            else:
                print(output)
            
            return data

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            print("Error: Authentication failed. Make sure you're using an ADMIN API key.", file=sys.stderr)
        else:
            print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        try:
            error_data = e.response.json()
            print(f"Details: {error_data}", file=sys.stderr)
        except Exception:
            print(f"Response: {e.response.text[:500]}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Request Error: {e}", file=sys.stderr)
        sys.exit(1)


def format_csv(results: list) -> str:
    """Format results as CSV."""
    if not results:
        return "No data"
    
    # Get headers from first result
    headers = list(results[0].keys())
    lines = [",".join(headers)]
    
    for row in results:
        values = []
        for h in headers:
            val = row.get(h, "")
            # Escape commas and quotes
            if isinstance(val, str) and ("," in val or '"' in val):
                val = f'"{val.replace(chr(34), chr(34)+chr(34))}"'
            values.append(str(val) if val is not None else "")
        lines.append(",".join(values))
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="View Venice AI usage history"
    )
    parser.add_argument(
        "--currency", "-c",
        choices=VALID_CURRENCIES,
        default="DIEM",
        help="Currency to filter by (default: DIEM)"
    )
    parser.add_argument(
        "--start-date",
        help="Start date filter (ISO format: 2024-01-01)"
    )
    parser.add_argument(
        "--end-date",
        help="End date filter (ISO format: 2024-12-31)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=50,
        help="Results per page, max 200 (default: 50)"
    )
    parser.add_argument(
        "--page", "-p",
        type=int,
        default=1,
        help="Page number (default: 1)"
    )
    parser.add_argument(
        "--sort", "-s",
        choices=["asc", "desc"],
        default="desc",
        help="Sort order (default: desc)"
    )
    parser.add_argument(
        "--format", "-f",
        dest="output_format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save output to file"
    )

    args = parser.parse_args()
    
    get_usage(
        currency=args.currency,
        start_date=args.start_date,
        end_date=args.end_date,
        limit=args.limit,
        page=args.page,
        sort_order=args.sort,
        output_format=args.output_format,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()

