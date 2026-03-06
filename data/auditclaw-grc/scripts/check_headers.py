#!/usr/bin/env python3
"""Security header audit for web applications.

Checks for the presence and configuration of important security headers.
Returns a score (0-100), grade (A-F), and per-header analysis.

Usage:
    python3 check_headers.py --url <url> [--format json|text]

Exit codes:
    0 = success (headers checked)
    1 = connection error
    2 = invalid URL
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print(json.dumps({
        "status": "error",
        "message": "requests library required. Install: pip3 install requests"
    }), file=sys.stderr)
    sys.exit(2)


# Security headers to check, with weight and severity if missing
SECURITY_HEADERS = {
    "Content-Security-Policy": {
        "weight": 25,
        "severity": "high",
        "description": "Controls resources the browser is allowed to load",
        "recommendation": "Add Content-Security-Policy header with appropriate directives"
    },
    "Strict-Transport-Security": {
        "weight": 20,
        "severity": "high",
        "description": "Enforces HTTPS connections",
        "recommendation": "Add Strict-Transport-Security: max-age=31536000; includeSubDomains"
    },
    "X-Frame-Options": {
        "weight": 15,
        "severity": "medium",
        "description": "Prevents clickjacking by controlling iframe embedding",
        "recommendation": "Add X-Frame-Options: DENY or SAMEORIGIN"
    },
    "X-Content-Type-Options": {
        "weight": 15,
        "severity": "medium",
        "description": "Prevents MIME type sniffing",
        "recommendation": "Add X-Content-Type-Options: nosniff"
    },
    "Referrer-Policy": {
        "weight": 10,
        "severity": "medium",
        "description": "Controls referrer information sent with requests",
        "recommendation": "Add Referrer-Policy: strict-origin-when-cross-origin"
    },
    "Permissions-Policy": {
        "weight": 15,
        "severity": "medium",
        "description": "Controls browser features available to the page",
        "recommendation": "Add Permissions-Policy to restrict camera, microphone, geolocation, etc."
    }
}


def validate_url(url):
    """Validate and normalize URL."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.hostname:
        return None
    return url


def check_headers(url):
    """Fetch URL and analyze security headers."""
    try:
        response = requests.get(url, timeout=15, allow_redirects=True,
                                headers={"User-Agent": "GRC-Compliance-Scanner/1.0"})
    except requests.exceptions.ConnectionError:
        return None, "Connection failed"
    except requests.exceptions.Timeout:
        return None, "Connection timed out"
    except requests.exceptions.RequestException as e:
        return None, str(e)

    headers_result = {}
    score = 0
    total_weight = 0
    recommendations = []

    for header_name, config in SECURITY_HEADERS.items():
        total_weight += config["weight"]
        value = response.headers.get(header_name)

        if value:
            headers_result[header_name] = {
                "present": True,
                "value": value,
                "severity": "ok"
            }
            score += config["weight"]
        else:
            headers_result[header_name] = {
                "present": False,
                "severity": config["severity"]
            }
            recommendations.append(config["recommendation"])

    # Normalize score to 0-100
    final_score = round((score / total_weight) * 100) if total_weight > 0 else 0

    # Grade assignment
    if final_score >= 90:
        grade = "A"
    elif final_score >= 75:
        grade = "B"
    elif final_score >= 60:
        grade = "C"
    elif final_score >= 40:
        grade = "D"
    else:
        grade = "F"

    return {
        "status": "ok",
        "url": url,
        "final_url": response.url,
        "status_code": response.status_code,
        "score": final_score,
        "grade": grade,
        "headers": headers_result,
        "recommendations": recommendations,
        "checked_at": datetime.now(timezone.utc).isoformat()
    }, None


def format_text(result):
    """Format results as human-readable text."""
    lines = [
        f"Security Header Scan: {result['url']}",
        f"Score: {result['score']}/100 (Grade: {result['grade']})",
        f"Checked: {result['checked_at']}",
        ""
    ]

    for name, info in result["headers"].items():
        if info["present"]:
            lines.append(f"  [OK] {name}: {info['value']}")
        else:
            lines.append(f"  [MISSING] {name} (severity: {info['severity']})")

    if result["recommendations"]:
        lines.append("\nRecommendations:")
        for rec in result["recommendations"]:
            lines.append(f"  - {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check security headers for a URL")
    parser.add_argument("--url", required=True, help="URL to check")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    args = parser.parse_args()

    url = validate_url(args.url)
    if not url:
        print(json.dumps({"status": "error", "message": f"Invalid URL: {args.url}"}),
              file=sys.stderr)
        sys.exit(2)

    result, error = check_headers(url)
    if error:
        print(json.dumps({"status": "error", "message": error}), file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
