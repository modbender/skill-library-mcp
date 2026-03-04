#!/usr/bin/env python3
"""Diff local DesignSpec model against current Figma file state."""

import argparse
import json
import logging
from pathlib import Path

from figma_common import api_get, setup_logging, stable_id, write_json
from figma_pull import normalize_node, extract_styles, extract_tokens

logger = logging.getLogger("figma-sync.diff")


def diff_properties(local_props: dict, remote_props: dict, path: str) -> list:
    """Compare two property dicts and return list of changes."""
    changes = []
    all_keys = sorted(set(list(local_props.keys()) + list(remote_props.keys())))

    for key in all_keys:
        local_val = local_props.get(key)
        remote_val = remote_props.get(key)

        if local_val == remote_val:
            continue

        if local_val is None:
            changes.append({
                "type": "added_remote",
                "path": f"{path}.{key}",
                "remoteValue": remote_val,
            })
        elif remote_val is None:
            changes.append({
                "type": "removed_remote",
                "path": f"{path}.{key}",
                "localValue": local_val,
            })
        else:
            changes.append({
                "type": "modified",
                "path": f"{path}.{key}",
                "localValue": local_val,
                "remoteValue": remote_val,
            })

    return changes


def diff_nodes(local_node: dict, remote_node: dict, path: str = "") -> list:
    """Recursively diff two DesignSpec nodes."""
    changes = []
    node_path = f"{path}/{local_node.get('name', '?')}"

    # Compare properties
    local_props = local_node.get("properties", {})
    remote_props = remote_node.get("properties", {})
    changes.extend(diff_properties(local_props, remote_props, node_path))

    # Compare children by figmaNodeId
    local_children = {c["figmaNodeId"]: c for c in local_node.get("children", [])}
    remote_children = {c["figmaNodeId"]: c for c in remote_node.get("children", [])}

    all_child_ids = sorted(set(list(local_children.keys()) + list(remote_children.keys())))
    for cid in all_child_ids:
        lc = local_children.get(cid)
        rc = remote_children.get(cid)
        if lc and rc:
            changes.extend(diff_nodes(lc, rc, node_path))
        elif lc and not rc:
            changes.append({
                "type": "removed_remote",
                "path": f"{node_path}/{lc['name']}",
                "description": f"Node {lc['name']} ({cid}) exists locally but not in Figma",
            })
        elif rc and not lc:
            changes.append({
                "type": "added_remote",
                "path": f"{node_path}/{rc['name']}",
                "description": f"Node {rc['name']} ({cid}) exists in Figma but not locally",
            })

    return changes


def changes_to_patch_spec(changes: list) -> dict:
    """Convert a list of changes into a minimal patch spec."""
    operations = []

    for change in changes:
        if change["type"] == "modified":
            path_parts = change["path"].rsplit(".", 1)
            if len(path_parts) == 2:
                prop_name = path_parts[1]
                if prop_name == "textContent":
                    operations.append({
                        "type": "setText",
                        "nodeId": _extract_node_id(change["path"]),
                        "value": change["remoteValue"],
                    })
                elif prop_name == "fills":
                    operations.append({
                        "type": "setFill",
                        "nodeId": _extract_node_id(change["path"]),
                        "value": change["remoteValue"],
                    })

    return {"operations": operations}


def _extract_node_id(path: str) -> str:
    """Best-effort extraction of a node identifier from a diff path."""
    parts = path.split("/")
    return parts[-1].split(".")[0] if parts else "unknown"


def diff(file_key: str, local_model_path: str, output_dir: str = "./out"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Load local model
    local_model = json.loads(Path(local_model_path).read_text())
    logger.info("Loaded local model: %s (%s)", local_model.get("fileName"), local_model.get("lastModified"))

    # Fetch current remote state
    logger.info("Fetching current file %s from Figma", file_key)
    data = api_get(f"/v1/files/{file_key}", file_key=file_key)
    document = data.get("document", {})

    # Normalize remote
    remote_frames = []
    remote_components = []
    for page in document.get("children", []):
        for child in page.get("children", []):
            if not isinstance(child, dict):
                continue
            normalized = normalize_node(child)
            if child.get("type") in ("COMPONENT", "COMPONENT_SET"):
                remote_components.append(normalized)
            else:
                remote_frames.append(normalized)

    # Diff frames
    all_changes = []
    local_frames = {f["figmaNodeId"]: f for f in local_model.get("frames", [])}
    remote_frames_map = {f["figmaNodeId"]: f for f in remote_frames}

    for fid in sorted(set(list(local_frames.keys()) + list(remote_frames_map.keys()))):
        lf = local_frames.get(fid)
        rf = remote_frames_map.get(fid)
        if lf and rf:
            all_changes.extend(diff_nodes(lf, rf))
        elif lf and not rf:
            all_changes.append({"type": "removed_remote", "path": f"/{lf['name']}", "description": f"Frame removed from Figma"})
        elif rf and not lf:
            all_changes.append({"type": "added_remote", "path": f"/{rf['name']}", "description": f"New frame in Figma"})

    # Diff components
    local_comps = {c["figmaNodeId"]: c for c in local_model.get("components", [])}
    remote_comps_map = {c["figmaNodeId"]: c for c in remote_components}

    for cid in sorted(set(list(local_comps.keys()) + list(remote_comps_map.keys()))):
        lc = local_comps.get(cid)
        rc = remote_comps_map.get(cid)
        if lc and rc:
            all_changes.extend(diff_nodes(lc, rc))
        elif lc and not rc:
            all_changes.append({"type": "removed_remote", "path": f"/{lc['name']}", "description": "Component removed from Figma"})
        elif rc and not lc:
            all_changes.append({"type": "added_remote", "path": f"/{rc['name']}", "description": "New component in Figma"})

    # Diff tokens
    local_tokens = local_model.get("tokens", {})
    remote_tokens = extract_tokens({"frames": remote_frames, "components": remote_components})
    token_changes = diff_properties(local_tokens, remote_tokens, "/tokens")
    all_changes.extend(token_changes)

    # Generate patch spec
    patch_spec = changes_to_patch_spec(all_changes)

    result = {
        "fileKey": file_key,
        "localLastModified": local_model.get("lastModified", ""),
        "remoteLastModified": data.get("lastModified", ""),
        "totalChanges": len(all_changes),
        "changes": all_changes,
        "patchSpec": patch_spec,
    }

    write_json(out / "diffResult.json", result)
    write_json(out / "patchSpec.json", patch_spec)

    logger.info("Diff complete: %d changes found", len(all_changes))
    return result


def main():
    parser = argparse.ArgumentParser(description="Diff local model against Figma")
    parser.add_argument("--file-key", required=True, help="Figma file key")
    parser.add_argument("--local-model", required=True, help="Path to local designModel.json")
    parser.add_argument("--output-dir", default="./out")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)
    diff(args.file_key, args.local_model, args.output_dir)


if __name__ == "__main__":
    main()
