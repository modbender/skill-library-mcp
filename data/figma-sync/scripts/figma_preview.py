#!/usr/bin/env python3
"""Preview what Figma operations would change (dry-run summary)."""

import argparse
import json
import logging
from pathlib import Path

from figma_common import api_get, setup_logging, write_json
from figma_push import validate_patch_spec, describe_operation, fetch_current_state, _summarize_node

logger = logging.getLogger("figma-sync.preview")


def preview(file_key: str, operations_path: str, output_dir: str = "./out"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Load operations
    ops_data = json.loads(Path(operations_path).read_text())
    if isinstance(ops_data, list):
        patch_spec = {"operations": ops_data}
    else:
        patch_spec = ops_data

    ops, warnings = validate_patch_spec(patch_spec)

    # Fetch current state of affected nodes
    node_ids = list(set(op["nodeId"] for op in ops if op.get("nodeId")))
    current_state = fetch_current_state(file_key, node_ids) if node_ids else {}

    preview_items = []
    for i, op in enumerate(ops):
        item = {
            "index": i,
            "type": op.get("type"),
            "description": describe_operation(op),
            "nodeId": op.get("nodeId"),
            "requiresPlugin": True,  # All node mutations need plugin
        }

        # Add current state if available
        nid = op.get("nodeId")
        if nid and nid in current_state:
            item["currentState"] = _summarize_node(current_state[nid])

        # Show what would change
        if op.get("type") == "setText":
            item["change"] = {
                "property": "characters",
                "currentValue": current_state.get(nid, {}).get("document", {}).get("characters"),
                "newValue": op.get("value"),
            }
        elif op.get("type") == "setFill":
            item["change"] = {
                "property": "fills",
                "newValue": op.get("value"),
            }
        elif op.get("type") == "setAutoLayout":
            item["change"] = {
                "property": "layoutMode",
                "newValue": op.get("value"),
            }
        elif op.get("type") in ("createComponent", "createFrame"):
            item["change"] = {
                "action": "create",
                "name": op.get("name"),
                "properties": op.get("properties", {}),
            }

        preview_items.append(item)

    result = {
        "fileKey": file_key,
        "totalOperations": len(ops),
        "operationsRequiringPlugin": len([p for p in preview_items if p.get("requiresPlugin")]),
        "warnings": warnings,
        "preview": preview_items,
        "summary": _build_summary(preview_items),
    }

    write_json(out / "preview.json", result)

    # Print human-readable summary
    print(f"\n{'='*60}")
    print(f"PREVIEW: {len(ops)} operations on file {file_key}")
    print(f"{'='*60}")
    for item in preview_items:
        status = "🔌 Plugin" if item.get("requiresPlugin") else "🌐 REST"
        print(f"  [{status}] {item['description']}")
        if item.get("change"):
            change = item["change"]
            if "currentValue" in change and change["currentValue"]:
                print(f"           Current: {str(change['currentValue'])[:60]}")
            if "newValue" in change:
                print(f"           New:     {str(change['newValue'])[:60]}")
    if warnings:
        print(f"\n⚠️  Warnings:")
        for w in warnings:
            print(f"  - {w}")
    print(f"{'='*60}\n")

    logger.info("Preview complete: %d operations", len(ops))
    return result


def _build_summary(items: list) -> dict:
    """Build a summary of operation types."""
    by_type = {}
    for item in items:
        t = item.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    return {"byType": by_type}


def main():
    parser = argparse.ArgumentParser(description="Preview Figma operations (dry-run)")
    parser.add_argument("--file-key", required=True, help="Figma file key")
    parser.add_argument("--operations", required=True, help="Path to operations JSON")
    parser.add_argument("--output-dir", default="./out")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)
    preview(args.file_key, args.operations, args.output_dir)


if __name__ == "__main__":
    main()
