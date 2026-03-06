#!/usr/bin/env python3
"""
Foxcode Endpoint Status Checker

Check the health and availability of all Foxcode endpoints.

Usage:
    python3 scripts/check_status.py              # Check all endpoints
    python3 scripts/check_status.py --endpoint official  # Check specific endpoint
    python3 scripts/check_status.py --format json        # JSON output
"""

import argparse
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from typing import Dict, List, Optional

# Endpoint definitions
ENDPOINTS = {
    "official": {
        "name": "Claude Code 官方专用线路",
        "url": "https://code.newcli.com/claude",
        "monitor_id": 2,
        "description": "Official dedicated line - highest reliability"
    },
    "super": {
        "name": "Super特价Claude Code",
        "url": "https://code.newcli.com/claude/super",
        "monitor_id": 5,
        "description": "Super discount tier - cost efficient"
    },
    "ultra": {
        "name": "Ultra特价Claude Code",
        "url": "https://code.newcli.com/claude/ultra",
        "monitor_id": 6,
        "description": "Ultra discount tier - maximum savings"
    },
    "aws": {
        "name": "AWS特价Claude Code",
        "url": "https://code.newcli.com/claude/aws",
        "monitor_id": 3,
        "description": "AWS infrastructure - fast response"
    },
    "aws-thinking": {
        "name": "AWS特价Claude Code（思考）",
        "url": "https://code.newcli.com/claude/droid",
        "monitor_id": 4,
        "description": "AWS with extended thinking - complex tasks"
    }
}

STATUS_PAGE_API = "https://status.rjj.cc/api/status-page/foxcode"


def check_endpoint_health(url: str, timeout: int = 10) -> Dict:
    """Check if an endpoint is reachable and measure response time."""
    start_time = time.time()
    try:
        req = Request(url, method="HEAD")
        req.add_header("User-Agent", "Foxcode-Status-Checker/1.0")

        with urlopen(req, timeout=timeout) as response:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "up",
                "status_code": response.getcode(),
                "response_time_ms": round(response_time, 2),
                "error": None
            }
    except HTTPError as e:
        response_time = (time.time() - start_time) * 1000
        # Some endpoints may return 404 for HEAD requests, which is okay
        if e.code in [404, 405]:
            return {
                "status": "up",
                "status_code": e.code,
                "response_time_ms": round(response_time, 2),
                "error": None
            }
        return {
            "status": "down",
            "status_code": e.code,
            "response_time_ms": round(response_time, 2),
            "error": str(e)
        }
    except URLError as e:
        return {
            "status": "down",
            "status_code": None,
            "response_time_ms": None,
            "error": str(e.reason)
        }
    except Exception as e:
        return {
            "status": "unknown",
            "status_code": None,
            "response_time_ms": None,
            "error": str(e)
        }


def fetch_status_page_data() -> Optional[Dict]:
    """Fetch data from the status page API."""
    try:
        req = Request(STATUS_PAGE_API)
        req.add_header("User-Agent", "Foxcode-Status-Checker/1.0")
        req.add_header("Accept", "application/json")

        with urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception:
        return None


def format_status_text(results: Dict[str, Dict]) -> str:
    """Format status results as human-readable text."""
    lines = [
        "=" * 70,
        "Foxcode Endpoint Status",
        "=" * 70,
        ""
    ]

    for key, endpoint in ENDPOINTS.items():
        result = results.get(key, {})
        status = result.get("status", "unknown")
        response_time = result.get("response_time_ms")
        error = result.get("error")

        # Status indicator
        if status == "up":
            indicator = "✓"
            status_text = "UP"
        elif status == "down":
            indicator = "✗"
            status_text = "DOWN"
        else:
            indicator = "?"
            status_text = "UNKNOWN"

        # Format response time
        if response_time is not None:
            time_str = f"{response_time:.0f}ms"
            if response_time < 500:
                time_color = "fast"
            elif response_time < 1000:
                time_str = f"{response_time:.0f}ms"
            else:
                time_str = f"{response_time:.0f}ms (slow)"
        else:
            time_str = "N/A"

        lines.append(f"{indicator} {endpoint['name']}")
        lines.append(f"  Status: {status_text}")
        lines.append(f"  URL: {endpoint['url']}")
        lines.append(f"  Response: {time_str}")
        if error:
            lines.append(f"  Error: {error}")
        lines.append(f"  {endpoint['description']}")
        lines.append("")

    lines.append("=" * 70)
    lines.append("Status Page: https://status.rjj.cc/status/foxcode")
    lines.append("=" * 70)

    return "\n".join(lines)


def format_status_json(results: Dict[str, Dict]) -> str:
    """Format status results as JSON."""
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "endpoints": {}
    }

    for key, endpoint in ENDPOINTS.items():
        result = results.get(key, {})
        output["endpoints"][key] = {
            "name": endpoint["name"],
            "url": endpoint["url"],
            "status": result.get("status", "unknown"),
            "response_time_ms": result.get("response_time_ms"),
            "error": result.get("error")
        }

    return json.dumps(output, indent=2)


def get_recommendation(results: Dict[str, Dict]) -> str:
    """Provide a recommendation based on current status."""
    working_endpoints = [
        key for key, result in results.items()
        if result.get("status") == "up"
    ]

    if not working_endpoints:
        return "⚠️  All endpoints appear to be down. Check your network connection."

    # Find fastest working endpoint
    fastest = None
    fastest_time = float('inf')

    for key in working_endpoints:
        response_time = results[key].get("response_time_ms")
        if response_time and response_time < fastest_time:
            fastest_time = response_time
            fastest = key

    recommendations = []

    if "official" in working_endpoints:
        recommendations.append(f"• Official endpoint is the safest choice for reliability")

    if fastest and fastest != "official":
        endpoint_name = ENDPOINTS[fastest]["name"]
        recommendations.append(f"• {endpoint_name} is currently fastest ({fastest_time:.0f}ms)")

    if "super" in working_endpoints or "ultra" in working_endpoints:
        recommendations.append(f"• Use Super or Ultra for cost savings")

    return "\n".join(recommendations)


def main():
    parser = argparse.ArgumentParser(
        description="Check Foxcode endpoint status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Check all endpoints
  %(prog)s --endpoint super   Check specific endpoint
  %(prog)s --format json    Output as JSON
        """
    )

    parser.add_argument(
        "--endpoint",
        choices=list(ENDPOINTS.keys()),
        help="Check a specific endpoint"
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()

    # Determine which endpoints to check
    if args.endpoint:
        endpoints_to_check = {args.endpoint: ENDPOINTS[args.endpoint]}
    else:
        endpoints_to_check = ENDPOINTS

    # Check each endpoint
    results = {}
    print("Checking endpoints...", file=sys.stderr)

    for key, endpoint in endpoints_to_check.items():
        results[key] = check_endpoint_health(endpoint["url"])

    # Output results
    if args.format == "json":
        print(format_status_json(results))
    else:
        print(format_status_text(results))
        print()
        print("Recommendations:")
        print(get_recommendation(results))

    # Exit with error code if any endpoint is down
    any_down = any(
        result.get("status") == "down"
        for result in results.values()
    )

    if any_down and not args.endpoint:
        sys.exit(1)


if __name__ == "__main__":
    main()
