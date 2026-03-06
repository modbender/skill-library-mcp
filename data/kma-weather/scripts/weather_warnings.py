#!/usr/bin/env python3
"""
KMA Weather Warnings Status

Retrieves current weather warnings status from Korea Meteorological Administration.

Shows nationwide summary of active warnings and advisories.

Requires KMA_SERVICE_KEY environment variable.
"""

import sys
import json
import argparse
from typing import Dict

# Import local modules
try:
    from kma_api import fetch_api, print_error
except ImportError:
    # Try relative import if run as script
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from kma_api import fetch_api, print_error


# API Configuration
BASE_URL = "https://apis.data.go.kr/1360000/WthrWrnInfoService"
ENDPOINT = "/getPwnStatus"


def fetch_warning_status() -> Dict:
    """
    Fetch current weather warning status from KMA API.

    Returns:
        dict: API response data

    Raises:
        Exception: On API errors
    """
    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "numOfRows": "10",
        "pageNo": "1",
        "dataType": "JSON",
    }

    return fetch_api(url, params)


def format_warning_status(data: Dict) -> str:
    """
    Format weather warning status data.

    Args:
        data: API response data

    Returns:
        str: Formatted text output
    """
    try:
        items = data["response"]["body"]["items"]["item"]
    except (KeyError, TypeError):
        return "Error: Invalid API response format"

    # Handle single item (dict) or multiple items (list)
    if isinstance(items, dict):
        item = items
    elif isinstance(items, list):
        item = items[0]
    else:
        return "✅ 현재 발효 중인 기상특보가 없습니다."

    # Build output
    output = []
    output.append("🚨 기상특보 현황")

    # Issue time
    if "tmFc" in item:
        tm_fc = str(item["tmFc"]).zfill(12)
        tm_formatted = f"{tm_fc[:4]}-{tm_fc[4:6]}-{tm_fc[6:8]} {tm_fc[8:10]}:{tm_fc[10:12]}"
        output.append(f"발표시각: {tm_formatted}")

    # Effective time
    if "tmEf" in item:
        tm_ef = str(item["tmEf"]).zfill(12)
        tm_ef_formatted = f"{tm_ef[:4]}-{tm_ef[4:6]}-{tm_ef[6:8]} {tm_ef[8:10]}:{tm_ef[10:12]}"
        output.append(f"발효시각: {tm_ef_formatted}")

    output.append("")

    # Current warnings (t6)
    if "t6" in item and item["t6"]:
        output.append("📍 현재 발효 중인 특보")
        t6_content = item["t6"].strip()
        if t6_content and t6_content != "o 없음":
            # Parse and format t6 content
            lines = t6_content.split("o ")
            for line in lines:
                line = line.strip()
                if line and line != "없음":
                    output.append(f"  • {line}")
        else:
            output.append("  ✅ 없음")
        output.append("")

    # Preliminary warnings (t7)
    if "t7" in item and item["t7"]:
        output.append("⚠️  예비특보")
        t7_content = item["t7"].strip()
        if t7_content and t7_content != "o 없음":
            # Parse and format t7 content
            lines = t7_content.split("o ")
            for line in lines:
                line = line.strip()
                if line and line != "없음":
                    output.append(f"  • {line}")
        else:
            output.append("  ✅ 없음")
        output.append("")

    # Other info
    if "other" in item and item["other"]:
        other_content = item["other"].strip()
        if other_content and other_content != "o 없음":
            output.append("ℹ️  기타")
            lines = other_content.split("o ")
            for line in lines:
                line = line.strip()
                if line and line != "없음":
                    output.append(f"  • {line}")

    return "\n".join(output)


def main():
    """Main entry point for warnings status script."""
    parser = argparse.ArgumentParser(
        description="Get current weather warnings status from Korea Meteorological Administration"
    )

    # Output options
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response"
    )

    args = parser.parse_args()

    try:
        # Fetch warning status
        data = fetch_warning_status()

        if args.json:
            # Output raw JSON
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            # Format and output text
            output = format_warning_status(data)
            print(output)

    except Exception as e:
        print_error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
