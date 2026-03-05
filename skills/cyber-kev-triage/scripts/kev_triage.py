#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


CRITICALITY_WEIGHT = {"critical": 3.0, "high": 2.0, "medium": 1.0, "low": 0.5}
MAX_INPUT_BYTES = 1_048_576


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prioritize vulnerabilities for patching.")
    parser.add_argument("--input", required=False, help="Path to JSON input.")
    parser.add_argument("--output", required=True, help="Path to output artifact.")
    parser.add_argument("--format", choices=["json", "md", "csv"], default="json")
    parser.add_argument("--dry-run", action="store_true", help="Run without side effects.")
    return parser.parse_args()


def load_payload(path: str | None, max_input_bytes: int = MAX_INPUT_BYTES) -> dict:
    if not path:
        return {}
    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(f"Input file not found: {data_path}")
    if data_path.stat().st_size > max_input_bytes:
        raise ValueError(f"Input file exceeds {max_input_bytes} bytes: {data_path}")
    return json.loads(data_path.read_text(encoding="utf-8"))


def build_asset_map(assets: list[dict]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for asset in assets:
        name = str(asset.get("name", "")).strip()
        if not name:
            continue
        criticality = str(asset.get("criticality", "medium")).lower().strip()
        mapped[name] = criticality if criticality in CRITICALITY_WEIGHT else "medium"
    return mapped


def score_vulnerability(vuln: dict, asset_map: dict[str, str]) -> dict:
    cve = str(vuln.get("cve", "UNKNOWN"))
    cvss = float(vuln.get("cvss", 5.0))
    known_exploited = bool(vuln.get("known_exploited", False))
    asset = str(vuln.get("asset", "unmapped"))
    criticality = asset_map.get(asset, "medium")

    score = cvss + (3.0 if known_exploited else 0.0) + CRITICALITY_WEIGHT.get(criticality, 1.0)
    if score >= 12:
        priority = "P1"
        due_days = 3
    elif score >= 9:
        priority = "P2"
        due_days = 7
    else:
        priority = "P3"
        due_days = 21

    return {
        "cve": cve,
        "asset": asset,
        "cvss": cvss,
        "known_exploited": known_exploited,
        "criticality": criticality,
        "score": round(score, 2),
        "priority": priority,
        "recommended_due_days": due_days,
    }


def render(result: dict, output_path: Path, fmt: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return

    if fmt == "md":
        lines = [
            f"# {result['summary']}",
            "",
            f"- status: {result['status']}",
            "",
            "## Priorities",
        ]
        for item in result["details"]["prioritized_vulnerabilities"]:
            lines.append(
                f"- {item['priority']} | {item['cve']} | asset={item['asset']} | "
                f"score={item['score']} | due={item['recommended_due_days']}d"
            )
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "priority",
                "cve",
                "asset",
                "cvss",
                "known_exploited",
                "criticality",
                "score",
                "recommended_due_days",
            ],
        )
        writer.writeheader()
        writer.writerows(result["details"]["prioritized_vulnerabilities"])


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)
    assets = payload.get("assets", [])
    vulns = payload.get("vulnerabilities", [])

    asset_map = build_asset_map(assets if isinstance(assets, list) else [])
    if not isinstance(vulns, list):
        vulns = []

    scored = [score_vulnerability(v, asset_map) for v in vulns]
    scored.sort(key=lambda row: row["score"], reverse=True)

    status = "ok" if scored else "warning"
    summary = (
        f"Ranked {len(scored)} vulnerabilities for patch triage"
        if scored
        else "No vulnerabilities supplied; produced empty triage output"
    )
    result = {
        "status": status,
        "summary": summary,
        "artifacts": [str(Path(args.output))],
        "details": {
            "prioritized_vulnerabilities": scored,
            "total_assets_mapped": len(asset_map),
            "dry_run": args.dry_run,
        },
    }

    render(result, Path(args.output), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
