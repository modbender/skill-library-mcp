#!/usr/bin/env python3
"""Thin wrapper to execute ReportStudio Community and capture its JSON output.

This script is meant to be used by the OpenClaw skill workflow so the agent can:
- run ReportStudio deterministically
- validate artifacts exist
- surface warnings clearly

It does NOT modify the input file.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--out-dir", default="./artifacts")
    p.add_argument("--formats", default="xlsx,pdf,pptx")
    p.add_argument("--topn", type=int, default=10)
    p.add_argument("--grain", choices=["day", "week", "month"], default="month")
    p.add_argument("--dim", default=None)
    p.add_argument("--measure", default=None)
    p.add_argument("--time-range", default=None)
    p.add_argument(
        "--repo-dir",
        default=None,
        help="Path to ReportStudio repo (if omitted, uses current python environment)",
    )
    return p.parse_args()


def main() -> None:
    ns = parse_args()

    cmd = [
        sys.executable,
        "-m",
        "reportstudio.cli.main",
        "--file",
        ns.file,
        "--prompt",
        ns.prompt,
        "--out-dir",
        ns.out_dir,
        "--formats",
        ns.formats,
        "--topn",
        str(ns.topn),
        "--grain",
        ns.grain,
    ]
    if ns.dim:
        cmd += ["--dim", ns.dim]
    if ns.measure:
        cmd += ["--measure", ns.measure]
    if ns.time_range:
        cmd += ["--time-range", ns.time_range]

    cwd = ns.repo_dir or None
    p = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)

    payload = json.loads(p.stdout)

    # Basic post-checks: artifacts exist
    for a in payload.get("artifacts", []):
        path = a.get("path")
        if path:
            if not Path(path).exists():
                raise SystemExit(f"Missing artifact: {path}")

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
