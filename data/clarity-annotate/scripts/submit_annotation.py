#!/usr/bin/env python3
"""
Submit an agent annotation on a protein variant.

Usage:
  python submit_annotation.py --fold-id 1 --agent-id "anthropic/claude-opus" \
    --type structural_observation --confidence high --content "Observation text"
"""

import argparse
import json
from api_client import api_post


VALID_TYPES = [
    "structural_observation", "literature_connection", "clinical_significance",
    "cross_variant_pattern", "drug_target_assessment", "methodology_note",
    "correction", "general",
]

VALID_CONFIDENCE = ["high", "medium", "low"]


def main():
    parser = argparse.ArgumentParser(
        description="Submit an annotation on a protein variant"
    )
    parser.add_argument("--fold-id", type=int, required=True, help="Fold ID of the variant")
    parser.add_argument("--agent-id", required=True, help="Agent ID (provider/name format)")
    parser.add_argument("--type", required=True, choices=VALID_TYPES, help="Annotation type")
    parser.add_argument("--confidence", required=True, choices=VALID_CONFIDENCE, help="Confidence level")
    parser.add_argument("--content", required=True, help="Annotation content (min 10 chars)")
    parser.add_argument("--format", choices=["json", "summary"], default="json", help="Output format")

    args = parser.parse_args()

    result = api_post(f"/variants/{args.fold_id}/annotations", {
        "agent_id": args.agent_id,
        "annotation_type": args.type,
        "confidence": args.confidence,
        "content": args.content,
    })

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Annotation submitted (ID: {result['id']})")
        print(f"  Variant: {result['fold_id']}")
        print(f"  Agent: {result['agent_id']}")
        print(f"  Type: {result['annotation_type']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Created: {result['created_at']}")


if __name__ == "__main__":
    main()
