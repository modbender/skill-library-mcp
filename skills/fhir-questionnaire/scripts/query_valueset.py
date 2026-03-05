#!/usr/bin/env python3
"""
Query LOINC answer lists and FHIR ValueSets.

This script helps discover answer options for LOINC codes and search for ValueSets.
It uses the tx.fhir.org terminology server which has comprehensive LOINC support.

Usage:
    # Find answer options for a LOINC code
    python query_valueset.py --loinc-code "72166-2"

    # Search for answer lists by text
    python query_valueset.py --search "smoking"

    # Expand a specific ValueSet
    python query_valueset.py --expand "http://loinc.org/vs/LL2201-3"
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional
from urllib import request, parse, error


# Default FHIR terminology server with comprehensive LOINC support
DEFAULT_SERVER = "https://tx.fhir.org/r4"


def lookup_loinc_answerlist(loinc_code: str, server_url: str = DEFAULT_SERVER) -> Optional[Dict[str, str]]:
    """
    Look up a LOINC code to find its associated answer list ID and display name.

    Args:
        loinc_code: The LOINC code (e.g., "72166-2")
        server_url: FHIR terminology server base URL

    Returns:
        Dictionary with 'answerlist_id' and 'display', or None if not found
    """
    params = {
        "system": "http://loinc.org",
        "code": loinc_code
    }

    url = f"{server_url}/CodeSystem/$lookup?{parse.urlencode(params)}"

    try:
        print(f"Accessing: {url}", file=sys.stderr)
        req = request.Request(url)
        req.add_header("Accept", "application/fhir+json")

        with request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        if data.get("resourceType") != "Parameters":
            print(f"Error: Expected Parameters resource, got {data.get('resourceType')}", file=sys.stderr)
            return None

        # Extract display name and answer list
        display = None
        answerlist_id = None

        for param in data.get("parameter", []):
            # Get display name
            if param.get("name") == "display":
                display = param.get("valueString")

            # Find the AnswerList property
            if param.get("name") == "property":
                parts = param.get("part", [])
                code_part = next((p for p in parts if p.get("name") == "code" and p.get("valueCode") == "AnswerList"), None)
                if code_part:
                    value_part = next((p for p in parts if p.get("name") == "value"), None)
                    if value_part:
                        answerlist_id = value_part.get("valueCode")

        if answerlist_id:
            return {
                "answerlist_id": answerlist_id,
                "display": display or f"LOINC {loinc_code}"
            }

        return None

    except error.HTTPError as e:
        print(f"HTTP Error {e.code} when accessing {url}", file=sys.stderr)
        print(f"Reason: {e.reason}", file=sys.stderr)
        if e.code == 404:
            print(f"LOINC code {loinc_code} not found on this server", file=sys.stderr)
        elif e.code == 403:
            print("Access forbidden - server may not allow this operation", file=sys.stderr)
        return None
    except error.URLError as e:
        print(f"Network error when accessing {url}", file=sys.stderr)
        print(f"Error details: {e.reason}", file=sys.stderr)
        if "SSL" in str(e.reason) or "ssl" in str(e.reason):
            print("SSL/TLS handshake failed - this server may not be accessible from your environment", file=sys.stderr)
            print("Try using an alternative server with --server flag:", file=sys.stderr)
            print("  --server https://hapi.fhir.org/baseR4", file=sys.stderr)
            print("  --server https://r4.ontoserver.csiro.au/fhir", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response from {url}", file=sys.stderr)
        print(f"Parse error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error when accessing {url}", file=sys.stderr)
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        return None


def expand_valueset(valueset_url: str, server_url: str = DEFAULT_SERVER) -> Optional[Dict]:
    """
    Expand a ValueSet to show all contained codes.

    Args:
        valueset_url: ValueSet canonical URL (e.g., "http://loinc.org/vs/LL2201-3")
        server_url: FHIR terminology server base URL

    Returns:
        Expanded ValueSet resource or None if not found
    """
    params = {
        "url": valueset_url
    }

    url = f"{server_url}/ValueSet/$expand?{parse.urlencode(params)}"

    try:
        print(f"Accessing: {url}", file=sys.stderr)
        req = request.Request(url)
        req.add_header("Accept", "application/fhir+json")

        with request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        if data.get("resourceType") == "OperationOutcome":
            print(f"Server returned OperationOutcome for {valueset_url}", file=sys.stderr)
            issues = data.get("issue", [])
            for issue in issues:
                print(f"  Issue: {issue.get('details', {}).get('text', 'Unknown error')}", file=sys.stderr)
            return None

        return data

    except error.HTTPError as e:
        print(f"HTTP Error {e.code} when accessing {url}", file=sys.stderr)
        print(f"Reason: {e.reason}", file=sys.stderr)
        if e.code == 404:
            print(f"ValueSet not found: {valueset_url}", file=sys.stderr)
        return None
    except error.URLError as e:
        print(f"Network error when accessing {url}", file=sys.stderr)
        print(f"Error details: {e.reason}", file=sys.stderr)
        if "SSL" in str(e.reason) or "ssl" in str(e.reason):
            print("SSL/TLS handshake failed - this server may not be accessible from your environment", file=sys.stderr)
            print("Try using an alternative server with --server flag:", file=sys.stderr)
            print("  --server https://hapi.fhir.org/baseR4", file=sys.stderr)
            print("  --server https://r4.ontoserver.csiro.au/fhir", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response from {url}", file=sys.stderr)
        print(f"Parse error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error when accessing {url}", file=sys.stderr)
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        return None


def search_valuesets(search_term: str, server_url: str = DEFAULT_SERVER, limit: int = 10) -> List[Dict]:
    """
    Search for ValueSets by title or name.

    Args:
        search_term: Search term for ValueSet title/name
        server_url: FHIR terminology server base URL
        limit: Maximum number of results

    Returns:
        List of ValueSet resources
    """
    params = {
        "title:contains": search_term,
        "_count": str(limit),
        "_summary": "true"
    }

    url = f"{server_url}/ValueSet?{parse.urlencode(params)}"

    try:
        print(f"Accessing: {url}", file=sys.stderr)
        req = request.Request(url)
        req.add_header("Accept", "application/fhir+json")

        with request.urlopen(req, timeout=30) as response:
            bundle = json.loads(response.read().decode())

        if bundle.get("resourceType") != "Bundle":
            print(f"Error: Expected Bundle, got {bundle.get('resourceType')}", file=sys.stderr)
            return []

        entries = bundle.get("entry", [])
        if not entries:
            print(f"No ValueSets found matching '{search_term}'", file=sys.stderr)

        return entries

    except error.HTTPError as e:
        print(f"HTTP Error {e.code} when accessing {url}", file=sys.stderr)
        print(f"Reason: {e.reason}", file=sys.stderr)
        return []
    except error.URLError as e:
        print(f"Network error when accessing {url}", file=sys.stderr)
        print(f"Error details: {e.reason}", file=sys.stderr)
        if "SSL" in str(e.reason) or "ssl" in str(e.reason):
            print("SSL/TLS handshake failed - this server may not be accessible from your environment", file=sys.stderr)
            print("Try using an alternative server with --server flag:", file=sys.stderr)
            print("  --server https://hapi.fhir.org/baseR4", file=sys.stderr)
            print("  --server https://r4.ontoserver.csiro.au/fhir", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response from {url}", file=sys.stderr)
        print(f"Parse error: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Unexpected error when accessing {url}", file=sys.stderr)
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        return []


def format_expansion(valueset: Dict, show_full: bool = False) -> str:
    """Format an expanded ValueSet showing answer options."""
    output = []

    # Header information
    output.append(f"ValueSet: {valueset.get('name', 'N/A')}")
    output.append(f"URL: {valueset.get('url', 'N/A')}")
    output.append(f"Version: {valueset.get('version', 'N/A')}")
    output.append("")

    # Get expansion
    expansion = valueset.get("expansion", {})
    contains = expansion.get("contains", [])

    if not contains:
        output.append("No codes found in expansion.")
        return "\n".join(output)

    output.append(f"Answer Options ({len(contains)} total):")
    output.append("-" * 80)

    # Format codes
    for item in contains:
        code = item.get("code", "")
        display = item.get("display", "")
        system = item.get("system", "")

        if show_full:
            output.append(f"Code:    {code}")
            output.append(f"Display: {display}")
            output.append(f"System:  {system}")
            output.append("-" * 80)
        else:
            output.append(f"  {code:<15} {display}")

    return "\n".join(output)


def format_fhir_codings(valueset: Dict) -> str:
    """Format expansion as FHIR Coding objects for use in Questionnaires."""
    expansion = valueset.get("expansion", {})
    contains = expansion.get("contains", [])

    codings = []
    for item in contains:
        codings.append({
            "system": item.get("system"),
            "code": item.get("code"),
            "display": item.get("display")
        })

    return json.dumps(codings, indent=2)


def format_questionnaire_item(loinc_code: str, loinc_display: str, valueset_url: str, valueset: Dict) -> str:
    """Format as a FHIR Questionnaire item with answerValueSet."""
    expansion = valueset.get("expansion", {})
    contains = expansion.get("contains", [])

    item = {
        "linkId": loinc_code.replace("-", "_"),
        "type": "choice",
        "code": [{
            "system": "http://loinc.org",
            "code": loinc_code,
            "display": loinc_display
        }],
        "text": loinc_display,
        "answerValueSet": valueset_url,
        "_answerValueSet_preview": {
            "description": f"This ValueSet contains {len(contains)} answer options",
            "options": [{"code": c.get("code"), "display": c.get("display")} for c in contains[:5]]
        }
    }

    return json.dumps(item, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Query LOINC answer lists and FHIR ValueSets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find answer options for a LOINC code
  python query_valueset.py --loinc-code "72166-2"

  # Get FHIR Coding format for use in Questionnaires
  python query_valueset.py --loinc-code "72166-2" --format fhir

  # Get as a Questionnaire item template
  python query_valueset.py --loinc-code "72166-2" --format questionnaire

  # Search for ValueSets by keyword
  python query_valueset.py --search "smoking"

  # Expand a specific ValueSet URL
  python query_valueset.py --expand "http://loinc.org/vs/LL2201-3"

  # Use a different FHIR server
  python query_valueset.py --loinc-code "72166-2" --server https://hapi.fhir.org/baseR4
        """
    )

    parser.add_argument("--loinc-code", help="LOINC code to look up (finds associated answer list)")
    parser.add_argument("--search", help="Search term for ValueSets")
    parser.add_argument("--expand", help="ValueSet URL to expand")
    parser.add_argument("--server", default=DEFAULT_SERVER, help=f"FHIR server URL (default: {DEFAULT_SERVER})")
    parser.add_argument("--format", choices=["table", "json", "fhir", "questionnaire"], default="table",
                       help="Output format (default: table)")
    parser.add_argument("--limit", type=int, default=10, help="Maximum search results (default: 10)")
    parser.add_argument("--full", action="store_true", help="Show full details in table format")

    args = parser.parse_args()

    # Validate arguments
    modes = [args.loinc_code, args.search, args.expand]
    if sum(bool(m) for m in modes) != 1:
        parser.error("Exactly one of --loinc-code, --search, or --expand must be specified")

    # Mode 1: Look up LOINC code and find its answer list
    if args.loinc_code:
        print(f"Looking up LOINC code: {args.loinc_code}", file=sys.stderr)
        print(f"Using server: {args.server}", file=sys.stderr)
        print("", file=sys.stderr)

        lookup_result = lookup_loinc_answerlist(args.loinc_code, args.server)

        if not lookup_result:
            print("", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            print(f"RESULT: No answer list found for LOINC code {args.loinc_code}", file=sys.stderr)
            print("", file=sys.stderr)
            print("This could mean:", file=sys.stderr)
            print("  1. This LOINC code has no standardized answer options", file=sys.stderr)
            print("  2. Network/server error prevented lookup (see error messages above)", file=sys.stderr)
            print("  3. The server doesn't have this LOINC code in its database", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            sys.exit(0)  # Exit successfully to not break parallel commands

        answerlist_id = lookup_result["answerlist_id"]
        loinc_display = lookup_result["display"]

        print(f"✓ Found answer list: {answerlist_id}", file=sys.stderr)
        print(f"✓ LOINC display: {loinc_display}", file=sys.stderr)
        print("", file=sys.stderr)

        # Expand the answer list
        valueset_url = f"http://loinc.org/vs/{answerlist_id}"
        print(f"Expanding ValueSet: {valueset_url}", file=sys.stderr)
        print("", file=sys.stderr)

        valueset = expand_valueset(valueset_url, args.server)

        if not valueset:
            print("", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            print(f"RESULT: Failed to expand ValueSet {valueset_url}", file=sys.stderr)
            print("Check error messages above for details", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            sys.exit(0)  # Exit successfully to not break parallel commands

        # Output in requested format
        if args.format == "json":
            print(json.dumps(valueset, indent=2))
        elif args.format == "fhir":
            print(format_fhir_codings(valueset))
        elif args.format == "questionnaire":
            print(format_questionnaire_item(args.loinc_code, loinc_display, valueset_url, valueset))
        else:  # table
            print(format_expansion(valueset, args.full))

    # Mode 2: Search for ValueSets
    elif args.search:
        results = search_valuesets(args.search, args.server, args.limit)

        if not results:
            print("No results found.", file=sys.stderr)
            sys.exit(0)  # Exit successfully to not break parallel commands

        if args.format == "json":
            print(json.dumps(results, indent=2))
        else:
            print(f"{'Title':<50} {'URL':<70}")
            print("-" * 120)
            for entry in results:
                resource = entry.get("resource", {})
                title = resource.get("title", resource.get("name", "N/A"))[:47]
                if len(resource.get("title", resource.get("name", "N/A"))) > 50:
                    title += "..."
                url = resource.get("url", "N/A")[:67]
                if len(resource.get("url", "N/A")) > 70:
                    url += "..."
                print(f"{title:<50} {url:<70}")

    # Mode 3: Expand a specific ValueSet
    elif args.expand:
        valueset = expand_valueset(args.expand, args.server)

        if not valueset:
            sys.exit(0)  # Exit successfully to not break parallel commands

        if args.format == "json":
            print(json.dumps(valueset, indent=2))
        elif args.format == "fhir":
            print(format_fhir_codings(valueset))
        else:  # table
            print(format_expansion(valueset, args.full))


if __name__ == "__main__":
    main()
