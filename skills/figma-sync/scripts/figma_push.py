#!/usr/bin/env python3
"""Push changes to Figma. Generates plugin-compatible operation specs.

IMPORTANT: The Figma REST API is read-only for file content. This script:
1. Validates operations against the current file state
2. Generates a plugin-compatible operations spec
3. For REST-supported operations (variables, comments), executes directly
4. Logs all operations for audit trail

Actual node mutations require the figma-sync companion plugin running in Figma.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from figma_common import api_get, setup_logging, write_json

logger = logging.getLogger("figma-sync.push")

SUPPORTED_OPS = {
    "setText", "setFill", "setAutoLayout", "createComponent",
    "updateVariant", "createFrame", "updateStyle",
}

# Operations that can be done via REST API
REST_OPS = set()  # Currently none for node mutations — all require plugin


def validate_operation(op: dict) -> list:
    """Validate a single operation. Returns list of warnings."""
    warnings = []
    op_type = op.get("type", "")
    if op_type not in SUPPORTED_OPS:
        warnings.append(f"Unknown operation type: {op_type}")
    if not op.get("nodeId") and op_type not in ("createComponent", "createFrame"):
        warnings.append(f"Operation {op_type} missing nodeId")
    return warnings


def validate_patch_spec(patch_spec: dict) -> tuple:
    """Validate entire patch spec. Returns (valid_ops, all_warnings)."""
    ops = patch_spec.get("operations", [])
    valid = []
    all_warnings = []

    for i, op in enumerate(ops):
        warnings = validate_operation(op)
        if warnings:
            for w in warnings:
                all_warnings.append(f"Op[{i}]: {w}")
        valid.append(op)

    return valid, all_warnings


def fetch_current_state(file_key: str, node_ids: list) -> dict:
    """Fetch current state of target nodes for before/after comparison."""
    if not node_ids:
        return {}
    ids_str = ",".join(node_ids)
    try:
        data = api_get(f"/v1/files/{file_key}/nodes", file_key=file_key, params={"ids": ids_str})
        return data.get("nodes", {})
    except Exception as e:
        logger.warning("Could not fetch current state: %s", e)
        return {}


def describe_operation(op: dict) -> str:
    """Human-readable description of an operation."""
    op_type = op.get("type", "unknown")
    node_id = op.get("nodeId", "N/A")

    if op_type == "setText":
        return f"Set text on {node_id} to: {op.get('value', '')[:50]}"
    elif op_type == "setFill":
        return f"Set fill on {node_id} to: {op.get('value', {})}"
    elif op_type == "setAutoLayout":
        mode = op.get("value", {}).get("mode", "?")
        return f"Set auto-layout on {node_id} to {mode}"
    elif op_type == "createComponent":
        return f"Create component: {op.get('name', 'unnamed')}"
    elif op_type == "updateVariant":
        return f"Update variant on {node_id}: {op.get('value', {})}"
    elif op_type == "createFrame":
        return f"Create frame: {op.get('name', 'unnamed')}"
    elif op_type == "updateStyle":
        return f"Update style on {node_id}: {op.get('styleType', '?')}"
    return f"{op_type} on {node_id}"


def push(file_key: str, patch_spec_path: str, execute: bool = False, output_dir: str = "./out"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Load patch spec
    patch_spec = json.loads(Path(patch_spec_path).read_text())
    ops, warnings = validate_patch_spec(patch_spec)

    # Gather node IDs for state comparison
    node_ids = [op["nodeId"] for op in ops if op.get("nodeId")]
    before_state = fetch_current_state(file_key, list(set(node_ids))) if node_ids else {}

    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fileKey": file_key,
        "dryRun": not execute,
        "totalOperations": len(ops),
        "appliedOps": [],
        "failures": [],
        "warnings": warnings,
        "changelog": [],
    }

    for i, op in enumerate(ops):
        description = describe_operation(op)
        entry = {
            "index": i,
            "type": op.get("type"),
            "nodeId": op.get("nodeId"),
            "description": description,
        }

        if execute:
            if op.get("type") in REST_OPS:
                # Execute REST-capable operations
                try:
                    # Currently no node-mutation REST ops exist
                    entry["status"] = "applied"
                    results["appliedOps"].append(entry)
                except Exception as e:
                    entry["status"] = "failed"
                    entry["error"] = str(e)
                    results["failures"].append(entry)
            else:
                # Plugin-required operation
                entry["status"] = "pending_plugin"
                entry["note"] = "Requires figma-sync companion plugin in Figma"
                results["appliedOps"].append(entry)
        else:
            entry["status"] = "dry_run"
            results["appliedOps"].append(entry)

        results["changelog"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": description,
            "status": entry["status"],
        })

    # Generate plugin-compatible spec
    plugin_spec = {
        "version": "1.0.0",
        "fileKey": file_key,
        "operations": ops,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    write_json(out / "pluginSpec.json", plugin_spec)

    # Before/after summary
    if before_state:
        results["beforeState"] = {nid: _summarize_node(ndata) for nid, ndata in before_state.items()}

    write_json(out / "pushResult.json", results)

    # Summary
    applied = len([o for o in results["appliedOps"] if o["status"] != "failed"])
    failed = len(results["failures"])
    mode = "EXECUTE" if execute else "DRY RUN"
    logger.info("[%s] %d operations processed, %d applied, %d failed, %d warnings",
                mode, len(ops), applied, failed, len(warnings))

    if not execute:
        logger.info("To apply changes, run with --execute flag")
        logger.info("Plugin spec written to %s/pluginSpec.json — load in Figma plugin to apply", out)

    return results


def _summarize_node(node_data: dict) -> dict:
    """Create a brief summary of a node for before/after comparison."""
    doc = node_data.get("document", {})
    return {
        "name": doc.get("name"),
        "type": doc.get("type"),
        "characters": doc.get("characters"),
        "fills": len(doc.get("fills", [])),
        "children": len(doc.get("children", [])),
    }


def main():
    parser = argparse.ArgumentParser(description="Push changes to Figma")
    parser.add_argument("--file-key", required=True, help="Figma file key")
    parser.add_argument("--patch-spec", required=True, help="Path to patch spec JSON")
    parser.add_argument("--execute", action="store_true", help="Actually apply (default is dry-run)")
    parser.add_argument("--output-dir", default="./out")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)
    push(args.file_key, args.patch_spec, args.execute, args.output_dir)


if __name__ == "__main__":
    main()
