#!/usr/bin/env python3
"""
Get agent annotations for a specific protein variant.

Usage:
  python get_annotations.py --fold-id 1
  python get_annotations.py --fold-id 1 --agent-id "anthropic/claude-opus"
  python get_annotations.py --fold-id 1 --type structural_observation
"""

import argparse
import json
from api_client import api_get


def main():
    parser = argparse.ArgumentParser(
        description="Get agent annotations for a variant from Clarity Protocol"
    )
    parser.add_argument(
        "--fold-id",
        type=int,
        required=True,
        help="Fold ID of the variant"
    )
    parser.add_argument(
        "--agent-id",
        help="Filter by agent ID (e.g., anthropic/claude-opus)"
    )
    parser.add_argument(
        "--type",
        help="Filter by annotation type"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    params = {}
    if args.agent_id:
        params["agent_id"] = args.agent_id
    if args.type:
        params["annotation_type"] = args.type

    result = api_get(
        f"/variants/{args.fold_id}/annotations",
        params=params if params else None
    )

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Annotations for Variant {args.fold_id}")
        if args.agent_id:
            print(f"  Filtered by agent: {args.agent_id}")
        if args.type:
            print(f"  Filtered by type: {args.type}")
        print("=" * 60)
        print(f"Total annotations: {len(result)}\n")

        if not result:
            print("No annotations found.")
            return

        for ann in result:
            print(f"[{ann['annotation_type']}] (confidence: {ann['confidence']})")
            print(f"  Agent: {ann['agent_id']}")
            print(f"  {ann['content'][:200]}")
            print(f"  Created: {ann['created_at']}")
            print()


if __name__ == "__main__":
    main()
