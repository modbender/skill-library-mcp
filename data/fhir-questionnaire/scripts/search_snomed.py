#!/usr/bin/env python3
"""
Search SNOMED CT codes using the SNOMED CT Browser API.

This script provides a simple interface to search for SNOMED CT codes that can be used
in FHIR Questionnaire items for clinical concepts, conditions, procedures, etc.

Usage:
    python search_snomed.py "diabetes"
    python search_snomed.py "hypertension" --limit 10
"""

import argparse
import json
import sys
from typing import Dict, List, Optional
from urllib import request, parse, error


def search_snomed(query: str, limit: int = 5, semantic_tag: Optional[str] = None) -> List[Dict]:
    """
    Search SNOMED CT codes using the FHIR terminology server.

    Args:
        query: Search term for SNOMED CT codes
        limit: Maximum number of results to return (default: 5)
        semantic_tag: Optional semantic tag to filter results (e.g., "disorder", "procedure")

    Returns:
        List of SNOMED CT code dictionaries with code, display, and additional info
    """
    # Using tx.fhir.org terminology server which supports SNOMED CT
    base_url = "https://tx.fhir.org/r4/CodeSystem/$lookup"

    # For searching, we'll use the ValueSet expand operation with a filter
    search_url = "https://tx.fhir.org/r4/ValueSet/$expand"

    # If filtering by semantic tag, request more results to account for filtering
    request_count = limit * 5 if semantic_tag else limit

    params = {
        "url": "http://snomed.info/sct?fhir_vs",
        "filter": query,
        "count": str(request_count)
    }

    url = f"{search_url}?{parse.urlencode(params)}"

    try:
        req = request.Request(url)
        req.add_header("Accept", "application/fhir+json")

        with request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        # Check for errors
        if data.get("resourceType") == "OperationOutcome":
            print(f"FHIR server returned an error:", file=sys.stderr)
            for issue in data.get("issue", []):
                print(f"  {issue.get('severity')}: {issue.get('diagnostics', 'Unknown error')}", file=sys.stderr)
            return []

        # Extract codes from expansion
        expansion = data.get("expansion", {})
        contains = expansion.get("contains", [])

        results = []
        for item in contains:
            code = item.get("code")
            display = item.get("display", "")

            # Extract semantic tag from display if present (appears in parentheses at end)
            semantic = ""
            clean_display = display
            if "(" in display and display.rstrip().endswith(")"):
                parts = display.rsplit("(", 1)
                if len(parts) == 2:
                    clean_display = parts[0].strip()
                    semantic = parts[1].rstrip(")")

            # Filter by semantic tag if specified (must match before limiting results)
            if semantic_tag and semantic_tag.lower() not in semantic.lower():
                continue

            results.append({
                "code": code,
                "system": "http://snomed.info/sct",
                "display": display,
                "property": {
                    "semanticTag": semantic,
                    "active": True,
                    "moduleId": ""
                }
            })

            # Stop when we have enough results after filtering
            if len(results) >= limit:
                break

        return results

    except error.HTTPError as e:
        print(f"HTTP Error {e.code} when accessing FHIR terminology server", file=sys.stderr)
        print(f"Reason: {e.reason}", file=sys.stderr)
        if e.code == 429:
            print("Rate limit exceeded. Please wait a moment and try again.", file=sys.stderr)
        return []
    except error.URLError as e:
        print(f"Error accessing FHIR terminology server: {e}", file=sys.stderr)
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
        output.append(f"{'Code':<20} {'Display':<50} {'Semantic Tag':<15}")
        output.append("-" * 85)

        for item in results:
            code = item["code"]
            display = item["display"][:47] + "..." if len(item["display"]) > 50 else item["display"]
            semantic = item["property"]["semanticTag"][:12] + "..." if len(item["property"]["semanticTag"]) > 15 else item["property"]["semanticTag"]
            output.append(f"{code:<20} {display:<50} {semantic:<15}")

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
        description="Search SNOMED CT codes for FHIR Questionnaires",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search_snomed.py "diabetes"
  python search_snomed.py "hypertension" --limit 10
  python search_snomed.py "appendectomy" --format fhir
  python search_snomed.py "asthma" --semantic-tag "disorder"

Common semantic tags:
  disorder, finding, procedure, body structure, substance, organism
        """
    )

    parser.add_argument("query", help="Search term for SNOMED CT codes")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results (default: 5)")
    parser.add_argument("--format", choices=["json", "table", "fhir"], default="json",
                       help="Output format (default: json)")
    parser.add_argument("--semantic-tag", help="Filter by semantic tag (e.g., disorder, procedure)")

    args = parser.parse_args()

    results = search_snomed(args.query, args.limit, args.semantic_tag)

    if not results:
        print("No results found or an error occurred.", file=sys.stderr)
        sys.exit(0)  # Exit successfully to not break parallel commands

    print(format_output(results, args.format))


if __name__ == "__main__":
    main()
