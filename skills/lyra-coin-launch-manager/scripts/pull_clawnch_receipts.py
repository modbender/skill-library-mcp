#!/usr/bin/env python3
"""Pull canonical launch receipts from Clawnch for one or more symbols.

Writes:
- <out>/<SYMBOL>_clawnch_receipt.json
- <out>/clawnch_receipts_summary.json

Usage:
  python pull_clawnch_receipts.py --symbols STARCORE,STARCOREX --out state

Notes:
- Uses https://clawn.ch/api/launches?limit=500
- Clawnch is authoritative; indexers may lag.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests


def fetch_launches(limit: int = 500) -> list[dict[str, Any]]:
    r = requests.get(f"https://clawn.ch/api/launches?limit={limit}", timeout=30)
    r.raise_for_status()
    j = r.json()
    return j.get("launches") or []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", required=True, help="Comma-separated symbols")
    ap.add_argument("--out", default="state", help="Output directory")
    args = ap.parse_args()

    wanted = {s.strip().upper() for s in args.symbols.split(",") if s.strip()}
    if not wanted:
        raise SystemExit("No symbols provided")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    launches = fetch_launches()

    found: dict[str, dict[str, Any]] = {}
    for L in launches:
        sym = (L.get("symbol") or "").upper()
        if sym in wanted and sym not in found:
            found[sym] = L

    summary = {
        "wanted": sorted(wanted),
        "found": sorted(found.keys()),
        "missing": sorted([s for s in wanted if s not in found]),
        "receipts": found,
    }

    for sym, rec in found.items():
        (out_dir / f"{sym}_clawnch_receipt.json").write_text(
            json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    (out_dir / "clawnch_receipts_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if summary["missing"]:
        print(f"[WARN] Missing: {', '.join(summary['missing'])}")
        raise SystemExit(2)

    print(f"[OK] Receipts written for: {', '.join(sorted(found.keys()))}")


if __name__ == "__main__":
    main()
