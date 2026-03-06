#!/usr/bin/env python3
"""Backfill anchor IDs/URLs into the append-only ledger.

This appends an anchor_update record; it does not rewrite past records.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # workspace root
LEDGER = ROOT / "state" / "lygo_mint_ledger.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hash", required=True)
    ap.add_argument("--channel", required=True, help="moltbook|moltx|discord|4claw|x")
    ap.add_argument("--id", required=True, help="post id or url")
    args = ap.parse_args()

    rec = {
        "ts": utc_now(),
        "kind": "anchor_update",
        "hash": args.hash,
        "channel": args.channel,
        "anchor_id": args.id,
    }

    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("OK")


if __name__ == "__main__":
    main()
