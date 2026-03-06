#!/usr/bin/env python3
"""Generate a portable anchor snippet for a minted hash.

This reads the canonical ledger if available.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]  # workspace root
CANON = ROOT / "state" / "lygo_mint_ledger_canonical.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hash", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--version", default="")
    args = ap.parse_args()

    rec = {}
    if CANON.exists():
        data = json.loads(CANON.read_text(encoding="utf-8"))
        # accept either list or dict
        if isinstance(data, list):
            for r in data:
                if str(r.get("hash") or r.get("LYGO_HASH_SHA256") or "") == args.hash:
                    rec = r
                    break
        elif isinstance(data, dict):
            rec = data.get(args.hash, {}) or {}

    title = args.title or rec.get("title") or rec.get("pack_name") or "PACK"
    version = args.version or rec.get("pack_version") or ""

    print(f"LYGO-MINT v1 | {title} | {version}".strip())
    print(f"HASH_SHA256: {args.hash}")
    if rec.get("champion"):
        print(f"CHAMPION: {rec['champion']}")
    if rec.get("anchor"):
        print(f"ANCHOR: {rec['anchor']}")
    print(f"GENERATED_AT_UTC: {utc_now()}")
    print("LEDGER: state/lygo_mint_ledger.jsonl")
    print("CANON: state/lygo_mint_ledger_canonical.json")
    print("ANCHORS: (fill after posting)")
    print("- moltbook: ")
    print("- moltx: ")
    print("- discord: ")
    print("- 4claw: ")


if __name__ == "__main__":
    main()
