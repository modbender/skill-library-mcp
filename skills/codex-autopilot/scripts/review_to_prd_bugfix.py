#!/usr/bin/env python3
"""Sync P0/P1 review findings into prd-items bugfix entries."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

SOURCE_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert review P0/P1 rows into PRD bugfix items.")
    parser.add_argument("--review-file", required=True, help="markdown review file path")
    parser.add_argument("--items-file", required=True, help="prd-items.yaml path")
    parser.add_argument("--version", default="", help="target version id; default uses meta.default_version")
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("invalid prd items yaml")
    return data


def dump_yaml(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def select_version(doc: dict[str, Any], version: str) -> dict[str, Any]:
    versions = doc.get("versions")
    if not isinstance(versions, list):
        raise ValueError("invalid prd items yaml: versions must be list")

    chosen = version
    if not chosen:
        meta = doc.get("meta", {})
        if isinstance(meta, dict):
            chosen = str(meta.get("default_version", ""))
    if not chosen:
        raise ValueError("missing target version")

    for item in versions:
        if isinstance(item, dict) and str(item.get("id", "")) == chosen:
            return item
    raise ValueError(f"version not found: {chosen}")


def normalize_id(source_id: str) -> str:
    return "BUG-" + re.sub(r"[^A-Za-z0-9]+", "-", source_id.strip()).strip("-").upper()


def parse_review_rows(content: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current_priority = ""

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("## "):
            if "P0" in line:
                current_priority = "P0"
            elif "P1" in line:
                current_priority = "P1"
            else:
                current_priority = ""
            continue

        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2:
            continue

        source_id = parts[0]
        title = parts[1] if len(parts) > 1 else ""
        if not SOURCE_ID_RE.match(source_id):
            continue
        if current_priority not in {"P0", "P1"}:
            continue
        if not title or title in {"问题", "------"}:
            continue

        rows.append(
            {
                "source_id": source_id,
                "priority": current_priority,
                "title": title,
                "source": parts[2] if len(parts) > 2 else "",
                "detail": parts[3] if len(parts) > 3 else "",
            }
        )

    return rows


def to_severity(priority: str) -> str:
    if priority == "P0":
        return "high"
    if priority == "P1":
        return "medium"
    return "low"


def main() -> int:
    args = parse_args()
    review_file = Path(args.review_file).resolve()
    items_file = Path(args.items_file).resolve()

    if not review_file.exists():
        raise FileNotFoundError(f"review file not found: {review_file}")
    if not items_file.exists():
        raise FileNotFoundError(f"items file not found: {items_file}")

    review_content = review_file.read_text(encoding="utf-8", errors="ignore")
    findings = parse_review_rows(review_content)

    doc = load_yaml(items_file)
    target = select_version(doc, args.version)
    bugfixes = target.get("bugfixes")
    if not isinstance(bugfixes, list):
        bugfixes = []
        target["bugfixes"] = bugfixes

    existing_source_ids = {
        str(item.get("source_id", "")).strip()
        for item in bugfixes
        if isinstance(item, dict)
    }

    added = 0
    for row in findings:
        if row["source_id"] in existing_source_ids:
            continue
        bugfixes.append(
            {
                "id": normalize_id(row["source_id"]),
                "type": "bugfix",
                "severity": to_severity(row["priority"]),
                "status": "todo",
                "title": row["title"],
                "source_id": row["source_id"],
                "source_priority": row["priority"],
                "source_review_file": review_file.name,
                "source_ref": row["source"],
                "source_detail": row["detail"],
                "regression_checks": [],
            }
        )
        existing_source_ids.add(row["source_id"])
        added += 1

    if added > 0:
        dump_yaml(items_file, doc)

    print(
        json.dumps(
            {
                "review_file": str(review_file),
                "items_file": str(items_file),
                "parsed_findings": len(findings),
                "added_bugfixes": added,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
