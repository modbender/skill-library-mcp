#!/usr/bin/env python3
"""
normalize_targets.py
Normalize Web3 targets (addresses/repos/packages/scope files) into one manifest.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
URL_RE = re.compile(r"^https?://")


def detect_target_type(value: str) -> str:
    if ADDRESS_RE.match(value):
        return "evm-address"
    if URL_RE.match(value):
        return "repo-url"
    if value.startswith("0x") and len(value) > 42:
        return "sui-object-or-package"
    p = Path(value)
    if p.exists():
        if p.is_dir():
            return "local-path"
        return "file"
    return "unknown"


def load_scope_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Scope JSON must be an object.")
    return data


def build_manifest(
    chain: str,
    raw_targets: list[str],
    scope_data: dict[str, Any] | None,
    label_prefix: str,
) -> dict[str, Any]:
    targets: list[dict[str, Any]] = []
    idx = 1

    for t in raw_targets:
        t = t.strip()
        if not t:
            continue
        ttype = detect_target_type(t)
        targets.append(
            {
                "id": f"{label_prefix}-{idx:03d}",
                "label": f"{label_prefix}-{idx:03d}",
                "type": ttype,
                "chain": chain,
                "value": t,
            }
        )
        idx += 1

    if scope_data:
        for item in scope_data.get("in_scope", []):
            if not isinstance(item, str):
                continue
            targets.append(
                {
                    "id": f"{label_prefix}-{idx:03d}",
                    "label": f"{label_prefix}-{idx:03d}",
                    "type": detect_target_type(item),
                    "chain": chain,
                    "value": item,
                    "source": "scope",
                }
            )
            idx += 1

    return {
        "schema_version": "1.0",
        "chain": chain,
        "target_count": len(targets),
        "targets": targets,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Normalize Web3 targets into a single JSON manifest.")
    p.add_argument("--chain", default="ethereum", help="Chain context for targets.")
    p.add_argument(
        "--targets",
        nargs="*",
        default=[],
        help="Raw targets (addresses, repo URLs, local paths, package IDs).",
    )
    p.add_argument("--targets-file", help="Text file with one target per line.")
    p.add_argument("--scope-json", help="Structured scope JSON (from parse_web3_scope.py).")
    p.add_argument("--label-prefix", default="target", help="Prefix for generated labels.")
    p.add_argument("--output", "-o", help="Output path for manifest JSON.")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    raw_targets = list(args.targets)
    if args.targets_file:
        lines = Path(args.targets_file).read_text(encoding="utf-8").splitlines()
        raw_targets.extend(line.strip() for line in lines if line.strip() and not line.startswith("#"))

    scope_data = None
    if args.scope_json:
        scope_data = load_scope_json(Path(args.scope_json))
        if scope_data.get("chains"):
            args.chain = scope_data["chains"][0]

    manifest = build_manifest(
        chain=args.chain,
        raw_targets=raw_targets,
        scope_data=scope_data,
        label_prefix=args.label_prefix,
    )

    payload = json.dumps(manifest, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(f"Manifest saved: {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
