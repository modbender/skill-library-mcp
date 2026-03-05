#!/usr/bin/env python3
"""
Get agent findings for a specific protein variant.

Usage:
  python get_findings.py --fold-id 1                        # All findings
  python get_findings.py --fold-id 1 --agent-type structural  # Specific agent
"""

import argparse
import json
from api_client import api_get


def main():
    parser = argparse.ArgumentParser(
        description="Get agent findings for a variant from Clarity Protocol"
    )
    parser.add_argument(
        "--fold-id",
        type=int,
        required=True,
        help="Fold ID of the variant"
    )
    parser.add_argument(
        "--agent-type",
        choices=["structural", "clinical", "literature", "synthesis"],
        help="Filter by agent type"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # Build query parameters
    params = {}
    if args.agent_type:
        params["agent_type"] = args.agent_type

    # Make API request
    result = api_get(
        f"/variants/{args.fold_id}/findings",
        params=params if params else None
    )

    # Output results
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        # Summary format - group by agent type
        findings_by_type = {}
        for finding in result:
            agent_type = finding["agent_type"]
            if agent_type not in findings_by_type:
                findings_by_type[agent_type] = []
            findings_by_type[agent_type].append(finding)

        print(f"Findings for Variant {args.fold_id}")
        print("=" * 60)
        print(f"Total findings: {len(result)}\n")

        for agent_type, findings in sorted(findings_by_type.items()):
            print(f"{agent_type.upper()} Agent ({len(findings)} findings)")
            print("-" * 60)

            for finding in findings:
                print(f"Finding ID: {finding['id']}")
                print(f"Created: {finding['created_at']}")

                if finding.get('summary'):
                    print(f"Summary: {finding['summary']}")

                print()


if __name__ == "__main__":
    main()
