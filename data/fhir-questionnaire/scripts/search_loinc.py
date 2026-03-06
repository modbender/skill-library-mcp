#!/usr/bin/env python3
"""
Search LOINC codes using the SearchLOINC API.

This script provides a simple interface to search for LOINC codes that can be used
in FHIR Questionnaire items to make questions conform to clinical standards.

Usage:
    python search_loinc.py "blood pressure"
    python search_loinc.py "depression screening" --limit 10
"""

import argparse
import json
import sys
from typing import Dict, List, Optional
from urllib import request, parse, error


def search_loinc(query: str, limit: int = 5) -> List[Dict]:
    """
    Search LOINC codes using the SearchLOINC API.

    Args:
        query: Search term for LOINC codes
        limit: Maximum number of results to return (default: 5)

    Returns:
        List of LOINC code dictionaries with code, display, and additional info
    """
    base_url = "https://clinicaltables.nlm.nih.gov/api/loinc_items/v3/search"

    params = {
        "terms": query,
        "maxList": str(limit),
        "df": "LOINC_NUM,COMPONENT,SYSTEM,SCALE_TYP,METHOD_TYP,CLASS"
    }

    url = f"{base_url}?{parse.urlencode(params)}"

    try:
        with request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        # API returns: [count, [codes], null, [details]]
        if len(data) < 4:
            return []

        count = data[0]
        codes = data[1]
        details = data[3]

        results = []
        for i, code in enumerate(codes):
            if i < len(details):
                detail = details[i]
                results.append({
                    "code": code,
                    "system": "http://loinc.org",
                    "display": detail[1] if len(detail) > 1 else "",  # COMPONENT
                    "property": {
                        "component": detail[1] if len(detail) > 1 else "",
                        "system_measured": detail[2] if len(detail) > 2 else "",
                        "scale": detail[3] if len(detail) > 3 else "",
                        "method": detail[4] if len(detail) > 4 else "",
                        "class": detail[5] if len(detail) > 5 else ""
                    }
                })

        return results

    except error.URLError as e:
        print(f"Error accessing SearchLOINC API: {e}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing API response: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return []


def format_output(results: List[Dict], output_format: str = "json") -> str:
    """Format search results for output."""
    if output_format == "json":
        return json.dumps(results, indent=2)

    elif output_format == "table":
        if not results:
            return "No results found."

        output = []
        output.append(f"{'Code':<15} {'Display':<50} {'System/Scale':<20}")
        output.append("-" * 85)

        for item in results:
            code = item["code"]
            display = item["display"][:47] + "..." if len(item["display"]) > 50 else item["display"]
            sys_scale = f"{item['property']['system_measured']}/{item['property']['scale']}"[:17] + "..." if len(f"{item['property']['system_measured']}/{item['property']['scale']}") > 20 else f"{item['property']['system_measured']}/{item['property']['scale']}"
            output.append(f"{code:<15} {display:<50} {sys_scale:<20}")

        return "\n".join(output)

    elif output_format == "fhir":
        # Format as FHIR Coding objects
        codings = []
        for item in results:
            codings.append({
                "system": item["system"],
                "code": item["code"],
                "display": item["display"]
            })
        return json.dumps(codings, indent=2)

    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Search LOINC codes for FHIR Questionnaires",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search_loinc.py "blood pressure"
  python search_loinc.py "depression screening" --limit 10
  python search_loinc.py "body weight" --format fhir
        """
    )

    parser.add_argument("query", help="Search term for LOINC codes")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results (default: 5)")
    parser.add_argument("--format", choices=["json", "table", "fhir"], default="json",
                       help="Output format (default: json)")

    args = parser.parse_args()

    results = search_loinc(args.query, args.limit)

    if not results:
        print("No results found or an error occurred.", file=sys.stderr)
        sys.exit(0)  # Exit successfully to not break parallel commands

    print(format_output(results, args.format))


if __name__ == "__main__":
    main()
