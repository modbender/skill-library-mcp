#!/usr/bin/env python3
"""Save STARCORE-family monitoring links into BOOKMARK BRAIN (Yandex).

Uses tools/bookmark_brain_add_url.py to save Clanker + Blockscout + Dexscreener links.

Usage:
  python bookmark_starcore_family.py --symbols STARCORE,STARCOREX,STARCORECOIN \
      --receipts state/starcore_family_receipts_summary.json \
      --folder "bookmark_bar/BOOKMARK BRAIN/OPS/Dashboards"

If --receipts is absent, will try to read per-symbol receipts in state/<SYM>_clawnch_receipt.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # .../workspace
STATE = ROOT / "state"
DEFAULT_FOLDER = "bookmark_bar/BOOKMARK BRAIN/OPS/Dashboards"


def load_receipts(symbols: list[str], receipts_path: Path | None) -> dict[str, dict]:
    data: dict[str, dict] = {}
    if receipts_path and receipts_path.exists():
        j = json.loads(receipts_path.read_text(encoding="utf-8"))
        recs = j.get("receipts") or {}
        for sym, rec in recs.items():
            data[sym.upper()] = rec
    else:
        for sym in symbols:
            p = STATE / f"{sym}_clawnch_receipt.json"
            if p.exists():
                try:
                    data[sym.upper()] = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    pass
    return data


def add_bookmark(folder: str, name: str, url: str):
    cmd = [
        "python",
        str(ROOT / "tools" / "bookmark_brain_add_url.py"),
        "--path",
        folder,
        "--name",
        name,
        "--url",
        url,
    ]
    subprocess.check_call(cmd)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", default="STARCORE,STARCOREX,STARCORECOIN", help="Comma-separated symbols")
    ap.add_argument("--receipts", help="Path to summary receipts JSON")
    ap.add_argument("--folder", default=DEFAULT_FOLDER, help="Bookmark folder path")
    args = ap.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    recs = load_receipts(symbols, Path(args.receipts) if args.receipts else None)
    if not recs:
        raise SystemExit("No receipts found to bookmark")

    for sym in symbols:
        rec = recs.get(sym)
        if not rec:
            continue
        contract = rec.get("contractAddress") or ""
        clanker = rec.get("clankerUrl") or (contract and f"https://clanker.world/clanker/{contract}")
        if clanker:
            add_bookmark(args.folder, f"Clanker — {sym} {contract[:6]}…{contract[-4:]}", clanker)
        if contract:
            add_bookmark(args.folder, f"Blockscout — {sym} {contract[:6]}…{contract[-4:]}", f"https://base.blockscout.com/address/{contract}")
            add_bookmark(args.folder, f"Dexscreener — {sym}", f"https://api.dexscreener.com/latest/dex/search/?q={contract}")

    print(f"[OK] Bookmarks added for: {', '.join([s for s in symbols if recs.get(s)])}")


if __name__ == "__main__":
    main()
